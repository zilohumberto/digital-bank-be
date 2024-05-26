import os
from dotenv import load_dotenv


load_dotenv()

ENVIRONMENT = os.getenv("ENVIRONMENT")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")

PG_DBS = {
    "user": POSTGRES_USER,
    "password": POSTGRES_PASSWORD,
    "db": POSTGRES_DB,
    "host": POSTGRES_HOST,
    "port": POSTGRES_PORT,
}

SQLALCHEMY_DATABASE_URI = (
    "postgresql://{user}:{password}@{host}:{port}/{db}?client_encoding=utf-8".format(
        **PG_DBS
    )
)
SQLALCHEMY_TRACK_MODIFICATIONS = False
STATEMENT_TIMEOUT = 105000
DEBUG_MODE = bool(os.getenv("DEBUG_MODE")) or False
API_KEY_FOREX = os.getenv("API_KEY_FOREX")
FEE_PERCENTAGE = 0.001  # 2 dollars for each 1000


TOKEN_LENGTH = os.getenv("TOKEN_LENGTH", default=3)
SECRET_KEY = os.getenv("SECRET_KEY")

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', 6379)
