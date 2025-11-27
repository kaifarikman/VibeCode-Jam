from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "VibeCode ML Service"
    
    # LLM Configuration
    # SciBox API - новый эндпоинт, доступен публично
    SCIBOX_API_KEY: str = "sk-c7K8ClMXslvPl6SRw2P9Ig"
    SCIBOX_API_BASE: str = "https://llm.t1v.scibox.tech/v1"
    
    # Model Names (для SciBox API)
    MODEL_AWQ: str = "qwen3-32b-awq" # General purpose
    MODEL_CODER: str = "qwen3-coder-30b-a3b-instruct-fp8" # Coding specialist
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
