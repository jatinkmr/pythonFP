import redis
import json
from datetime import datetime

from config.settings import REDIS_HOST, REDIS_PORT


redisStore = redis.Redis(
    host=f"{REDIS_HOST}", port=REDIS_PORT, db=0, decode_responses=True
)

try:
    redisStore.ping()
    print("✅ Redis Connected successfully!!")
except redis.ConnectionError:
    print("❌ Unable to connect with Redis!!")
