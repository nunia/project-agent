from dotenv import load_dotenv
import os
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()

# Get OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY", "NONE")

class Settings(BaseSettings):
    # Other settings...
    OPENAI_API_KEY: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str

    class Config:
        env_file = ".env"

settings = Settings()
