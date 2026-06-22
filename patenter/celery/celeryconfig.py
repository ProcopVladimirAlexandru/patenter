from patenter.config.config import config


broker_url = config.KEYDB_CELERY_BROKER_URL
result_backend = config.KEYDB_CELERY_BROKER_URL
broker_transport_options = {"visibility_timeout": 43200}
result_backend_transport_options = {"visibility_timeout": 43200}
visibility_timeout = 43200
