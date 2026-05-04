from dataclasses import dataclass
from functools import lru_cache
import os


from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    ollama_url: str
    api_url: str
    email_webhook: str
    todo_webhook: str
    default_model: str = "llama3.2"
    connect_timeout: float = 10.0
    read_timeout: float = 180.0   
    write_timeout: float = 30.0
    pool_timeout: float = 10.0


@lru_cache
def get_settings() -> Settings:
    return Settings(
        ollama_url=os.getenv("OLLAMA_URL", "").strip(),
        api_url=os.getenv("API_URL", "http://127.0.0.1:8000/chat").strip(),
        email_webhook=os.getenv("EMAIL_WEBHOOK", "").strip(),
        todo_webhook=os.getenv("TODO_WEBHOOK", "").strip(),
        default_model=os.getenv("DEFAULT_MODEL", "llama3.2").strip(),
        connect_timeout=float(os.getenv("CONNECT_TIMEOUT", "10")),
        read_timeout=float(os.getenv("READ_TIMEOUT", "180")),
        write_timeout=float(os.getenv("WRITE_TIMEOUT", "30")),
        pool_timeout=float(os.getenv("POOL_TIMEOUT", "10"))
    )
