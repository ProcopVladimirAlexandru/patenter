# A Patent Infringement Search Tool Using FastAPI, Celery and OpenAI LLMs
Celery is configured to run with Redis as task sync tool and backend. Run Redis in Docker:
```
docker run --name patenter-redis -p 6379:6379 -d redis:8.8.0
```

Running Celery workers, from root of project:
```
celery -A patenter.celery.tasks worker --loglevel=INFO
```

Export the following environment variables:
```bash
# required
export OPENAI_API_KEY="..."
export ALLOW_ORIGINS="*" # or something more secure (comma separate your origins)
export DB_FILE_PATH="data/PatentData.json"

# optional
export MODEL_UID="gpt-5.5"
export OPENAI_REQUEST_TIMEOUT_S="600"
export OPENAI_MAX_RETRIES="5"
export OPENAI_TEMPERATURE="0.0"

```

It is recommended to use the Python version from `.python-version`.
Install the dependencies with:
```bash
pip install -r requirements.txt
```

To run the server in development mode, from root of project:
```bash
fastapi dev --port 8444
```
