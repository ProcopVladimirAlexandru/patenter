# Trying out some stuff
Running redis in docker:
```
docker run --name platformer-redis -p 6379:6379 -d redis:8.8.0
```

Running celery:
```
celery -A patenter.celery.tasks worker --loglevel=INFO
```