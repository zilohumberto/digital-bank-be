import os
import binascii
from cryptography.fernet import Fernet

import settings


class KeyProducerService:
    fernet = Fernet(settings.SECRET_KEY)
    """
        A charge to generate key from TOKEN_LENGTH * 2
    """
    @staticmethod
    def generate_key():
        # generate a token
        return binascii.hexlify(os.urandom(settings.TOKEN_LENGTH)).decode()

    @classmethod
    def make_password(cls, password: str):
        return cls.fernet.encrypt(password.encode()).decode()

    @classmethod
    def get_password(cls, password: str):
        return cls.fernet.decrypt(password.encode()).decode()
