import os
import uvicorn
import time
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from patenter.routers.v1.patents.router import router as patents_router
from patenter.config.config import config


logging.basicConfig(level=config.LOG_LEVEL)

app = FastAPI(tags=["patenter"])
app.include_router(patents_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOW_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8444)
