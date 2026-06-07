import logging

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
)
from patenter.config.config import config


logger = logging.getLogger(__name__)
SYSTEM_PROMPT: str = """You are a researcher specializing in patent infringement detection. Be thorough, accurate and attentive to detail in your analysis. Use your extensive knowledge of existing products and technologies."""


class InfringementDetectionsStructuredOutput(BaseModel):
    detections: list[InfringementDetectionModel]


class InfringementDetector:
    def __init__(self, patent: PatentModel):
        self.patent = patent

    def run(self) -> InfringementDetectionsModel:
        llm: BaseChatModel = ChatOpenAI(
            model_name=config.MODEL_UID,
            openai_api_key=config.OPENAI_API_KEY,
            temperature=config.OPENAI_TEMPERATURE,
            timeout=config.OPENAI_REQUEST_TIMEOUT_S,
            max_retries=config.OPENAI_MAX_RETRIES,
            rate_limiter=None,
        )
        tools: list = []
        agent = create_agent(
            model=llm,
            tools=tools,
            response_format=InfringementDetectionsStructuredOutput,
            system_prompt=SYSTEM_PROMPT,
        )
        # TODO
        prompt_template = ChatPromptTemplate(
            [
                ("system", SYSTEM_PROMPT),
                (
                    "human",
                    """Name existing products or technologies which potentially infringe on the following patent:
    \"{patent_text}\"
""",
                ),
            ]
        )
        prompt_value: ChatPromptValue = prompt_template.invoke(
            {"patent_text": self._get_full_patent_text_for_prompt()}
        )
        logger.debug("Will prompt model with:\n%s", prompt_value)

        # opt: switch to sqlalchemy celery backend so we can store patent information together with job
        llm_results = agent.invoke(prompt_value)
        return InfringementDetectionsModel(
            patent=self.patent,
            detections=llm_results["structured_response"].detections,
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
