# A Patent Infringement Search Tool Using FastAPI, Celery and OpenAI LLMs
Celery is configured to run with Redis as task sync tool and backend. Run Redis in Docker:
```
docker run --name patenter-redis -p 6379:6379 -d redis:8.8.0
```

Running Celery workers:
```
celery -A patenter.celery.tasks worker --loglevel=INFO
```

Export the following environment variables:
```
export OPENAI_API_KEY=""
```