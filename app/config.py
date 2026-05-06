from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ollama_url: str
    api_url: str 
    email_webhook: str
    todo_webhook: str

    default_model: str = "llama3.2"

    connect_timeout: float = 10.0
    read_timeout: float = 180.0
    write_timeout: float = 30.0
    pool_timeout: float = 10.0

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()