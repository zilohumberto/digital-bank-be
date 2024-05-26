import json
from flask import g

from application.services.cache_service import CacheService
from application.services.key_producer_service import KeyProducerService


class AuthService:

    def __init__(self):
        self.cache = CacheService()
        self.key_producer = KeyProducerService()

    def create_token(self, value: dict, prefix: str = "auth", exp=None):
        key = self.key_producer.generate_key()
        self.cache.set(key=f"{prefix}:{key}", value=json.dumps(value), exp=exp)
        return key

    def check_password(self, user, input_password):
        encrypt_user_password = user.password
        decrypt_user_password = self.key_producer.get_password(encrypt_user_password)
        if decrypt_user_password == input_password:
            return True, self.create_token({"id": str(user.id), "profile": user.profile, "email": user.email})
        return False, None

    def validate_token(self, token: str, prefix: str = "auth"):
        key = f"{prefix}:{token}"
        if self.cache.exists(key):
            return json.loads(self.cache.get(key))
        return None

    @staticmethod
    def is_admin() -> bool:
        if hasattr(g, "profile") and getattr(g, "profile") == "admin":
            return True
        return False
