import redis

from settings import REDIS_HOST, REDIS_PORT

class CacheService:
    def __init__(self):
        self.redis = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

    def set(self, key: str, value: str, exp=None):
        self.redis.set(key, value, ex=exp)

    def get(self, key: str):
        return self.redis.get(key)

    def exists(self, key: str):
        return self.redis.exists(key)

    def delete(self, key: str):
        self.redis.delete(key)
