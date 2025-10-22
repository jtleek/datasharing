"""
Configuration management for Brazilian Federal Data Collector SaaS
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    APP_NAME: str = "Brazilian Federal Data Collector SaaS"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/datasharing"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 0

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # Security
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # API Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000

    # Brazilian Data Sources
    DADOS_GOV_BR_BASE_URL: str = "https://dados.gov.br"
    PORTAL_TRANSPARENCIA_BASE_URL: str = "https://api.portaldatransparencia.gov.br/api-de-dados"
    IBGE_API_BASE_URL: str = "https://servicodados.ibge.gov.br/api/v3"

    # Data Storage
    DATA_STORAGE_PATH: str = "/data/datasets"
    MAX_DATASET_SIZE_MB: int = 1000
    SUPPORTED_FORMATS: str = "json,csv,parquet"

    # AI Features
    ENABLE_AUTO_PREPROCESSING: bool = True
    DEFAULT_AI_FORMAT: str = "parquet"

    @field_validator('SUPPORTED_FORMATS')
    @classmethod
    def parse_supported_formats(cls, v: str) -> List[str]:
        if isinstance(v, str):
            return [fmt.strip() for fmt in v.split(',')]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
