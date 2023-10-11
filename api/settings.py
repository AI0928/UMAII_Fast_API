from pydantic.v1 import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    secret_key: str

    class Config:
        env_file = ".env"
 

@lru_cache
def get_settings():
    return Settings()