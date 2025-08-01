# Redis connection helper

import redis
from rq import Queue

redis_conn = redis.Redis(host='localhost', port=6379, db=0)
q = Queue('crm_events', connection=redis_conn)