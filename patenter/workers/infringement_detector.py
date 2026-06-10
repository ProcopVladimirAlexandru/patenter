import logging
from typing import Any

from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel
from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompt_values import ChatPromptValue
from pydantic import BaseModel

from patenter.models.patents import PatentModel
from patenter.models.infringement_detections import (
    InfringementDetectionModel,
    InfringementDetectionsModel,
    InfringementDetectionPerClaimModel,
)
from patenter.config.config import config


logger = logging.getLogger(__name__)
SYSTEM_PROMPT: str = """You are a researcher specializing in patent infringement detection. Be thorough, accurate and attentive to detail in your analysis. Use your extensive knowledge of existing products and technologies. Search the web to identify the pages where infringing products are described"""


class InfringementDetectionStructuredOutput(BaseModel):
    infringing_enterprise: str
    infringing_product: str
    url: str
    per_claim_analysis: list[InfringementDetectionPerClaimModel]


class InfringementDetectionsStructuredOutput(BaseModel):
    detections: list[InfringementDetectionStructuredOutput]


class InfringementDetector:
    def __init__(
        self,
        patent: PatentModel,
        reasoning_effort: str,
        search_context_size: str,
        external_web_access: bool = True,
        model_uid: str | None = None,
        max_tokens: int = 100000,
    ):
        self.patent = patent
        self.model_uid: str = model_uid or config.MODEL_UID
        self.external_web_access: bool = external_web_access
        self.reasoning_effort: str = reasoning_effort
        self.search_context_size: str = search_context_size
        self.max_tokens: int = max_tokens

    def run(self) -> InfringementDetectionsModel:
        model_init_kwargs: dict[str, Any] = {
            "model_name": self.model_uid,
            "openai_api_key": config.OPENAI_API_KEY,
            "timeout": config.OPENAI_REQUEST_TIMEOUT_S,
            "max_retries": config.OPENAI_MAX_RETRIES,
            "rate_limiter": None,
            "reasoning_effort": self.reasoning_effort,
            "max_tokens": self.max_tokens,
            # this parameter to be balanced with cost, default is limited to 'return token budget' (research this more)
            # "return_token_budget": "unlimited"
        }
        if self.model_uid.startswith("gpt-"):
            model_init_kwargs["temperature"] = config.OPENAI_TEMPERATURE

        llm: BaseChatModel = ChatOpenAI(**model_init_kwargs)
        tools: list[dict] = [
            # See more: https://developers.openai.com/api/docs/guides/tools-web-search
            {
                "type": "web_search",
                "search_context_size": self.search_context_size,
                "external_web_access": self.external_web_access,
            }
        ]
        agent = create_agent(
            model=llm,
            tools=tools,
            response_format=InfringementDetectionsStructuredOutput,
        )
        prompt_template = ChatPromptTemplate(
            [
                ("system", SYSTEM_PROMPT),
                (
                    "human",
                    """Find existing products or technologies which potentially infringe on the following patent owned by {patent_assignees}:
    \"{patent_text}\"
""",
                ),
            ]
        )
        prompt_value: ChatPromptValue = prompt_template.invoke(
            {
                "patent_text": self._get_full_patent_text_for_prompt(),
                "patent_assignees": self._get_full_patent_assignees(),
            }
        )
        logger.debug("Will prompt model with:\n%s", prompt_value)

        # opt: switch to sqlalchemy celery backend so we can store patent information together with job
        llm_results = agent.invoke(prompt_value)

        return InfringementDetectionsModel(
            patent=self.patent,
            detections=[
                InfringementDetectionModel(model_uid=self.model_uid, **m.model_dump())
                for m in llm_results["structured_response"].detections
            ],
        )

    def _get_full_patent_text_for_prompt(self, abstract_only: bool = False) -> str:
        if abstract_only:
            return self.patent.abstract

        claims: list[str] = []
        for claim in self.patent.claims:
            claim_rows: list[str] = [f"Claim {claim.number}:"]
            if claim.preamble:
                claim_rows.append(claim.preamble)
            for element in claim.elements:
                claim_rows.append(f"- {element}")
            claims.append("\n".join(claim_rows))

        return self.patent.title + "\n" + "\n\n".join(claims)

    def _get_full_patent_assignees(self) -> str:
        if not len(self.patent.assignees):
            raise ValueError("Patent must have at least one assignee")
        return ", ".join(self.patent.assignees)
