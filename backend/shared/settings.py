from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Environment-driven configuration for API keys and tokens."""

    GITHUB_TOKEN: str = ""
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
