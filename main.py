import os
import uvicorn
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from patenter.routers.v1.patents.router import router as patents_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(tags=["patenter"], lifespan=lifespan)


app.include_router(patents_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOW_ORIGINS", "").split(",")
    if os.getenv("ALLOW_ORIGINS", None)
    else [],
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
