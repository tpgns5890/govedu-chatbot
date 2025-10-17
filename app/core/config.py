import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    APP_ENV: str = os.getenv("APP_ENV", "dev")
    DATA_DIR: str = os.getenv("DATA_DIR", "./data")
    SQLITE_PATH: str = os.getenv("SQLITE_PATH", "./data/structured/edu.db")
    VECTOR_DIR: str = os.getenv("VECTOR_DIR", "./data/vector")
    LOG_DB_PATH: str = os.getenv("LOG_DB_PATH", "./data/logs/chatlog.db")
    MODEL_PATH: str = os.getenv("MODEL_PATH", "./models/llama3-8b.gguf")

settings = Settings()
