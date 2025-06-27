import redis
import json
from datetime import datetime

redisStore = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

try:
    redisStore.ping()
    print("✅ Redis Connected successfully!!")
except redis.ConnectionError:
    print("❌ Unable to connect with Redis!!")
