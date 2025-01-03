from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Database
    DATABASE_URL: str = "sqlite:///./test.db"
    POSTGRES_USER: str = "testuser"
    POSTGRES_PASSWORD: str = "testpassword"
    POSTGRES_DB: str = "vectordb"
    POSTGRES_HOST: str = "localhost"

    # Docker
    DOCKER_RUNNING: bool = False

    # API
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Jira Agent API"

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    # Jira
    JIRA_BASE_URL: str
    JIRA_API_TOKEN: str
    JIRA_USERNAME: str
    PROJECT_KEY: str = "KA-01"
    JIRA_CLOUD: bool = True

    # OpenAI
    OPENAI_API_KEY: str

    # Environment
    ENV: str = "development"
    DEBUG: bool = True

    class Config:
        case_sensitive = True
        env_file = ".env"

    @property
    def get_database_url(self) -> str:
        """Get the database URL based on the environment"""
        if self.DOCKER_RUNNING:
            return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@db:5432/{self.POSTGRES_DB}"
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:5432/{self.POSTGRES_DB}"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
