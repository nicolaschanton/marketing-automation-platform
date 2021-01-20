import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "please_marketing.settings")
django.setup()
from please_marketing_app.models import *
import redis
from rq import Worker, Queue, Connection

listen = ['high', 'default', 'low']

redis_url = os.getenv('HEROKU_REDIS_ORANGE_URL', 'redis://localhost:6379')

conn_etl = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn_etl):
        worker_etl = Worker(map(Queue, listen))
        worker_etl.work()
