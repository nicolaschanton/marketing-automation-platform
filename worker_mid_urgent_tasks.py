import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "please_marketing.settings")
django.setup()
from please_marketing_app.models import *
import redis
from rq import Worker, Queue, Connection

listen = ['high', 'default', 'low']

redis_url = os.getenv('HEROKU_REDIS_WHITE_URL', 'redis://localhost:6379')

conn_mid_urgent_tasks = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn_mid_urgent_tasks):
        worker_mid_urgent_tasks = Worker(map(Queue, listen))
        worker_mid_urgent_tasks.work()
