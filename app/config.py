from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str
    MONGO_URI: str
    MONGO_DB_NAME: str
    model_config = SettingsConfigDict(env_file="products_service/.env", env_file_encoding='utf-8')

@lru_cache()
def get_settings(): return Settings()
settings = get_settings()