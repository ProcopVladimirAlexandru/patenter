import os
import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from platformer.routers.v1.reports import reports


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(tags=["platformer"], lifespan=lifespan)


app.include_router(reports.router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOW_ORIGINS", "").split(",")
    if os.getenv("ALLOW_ORIGINS", None)
    else [],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8444)
