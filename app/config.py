import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    BEDROCK_MODEL_ID: str = os.getenv(
        "BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0"
    )
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "sqlite+aiosqlite:///./mental_health.db"
    )


settings = Settings()
