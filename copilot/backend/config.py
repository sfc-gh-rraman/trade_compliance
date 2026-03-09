from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "Trade Compliance Platform"
    debug: bool = False
    
    snowflake_connection_name: str = "my_snowflake"
    snowflake_database: str = "TRADE_COMPLIANCE_DB"
    snowflake_schema: str = "TRADE_COMPLIANCE"
    snowflake_warehouse: str = "TRADE_COMPLIANCE_WH"
    snowflake_token: Optional[str] = None
    snowflake_host: Optional[str] = None
    
    semantic_model_path: str = "@TRADE_COMPLIANCE_DB.TRADE_COMPLIANCE.SEMANTIC_MODELS/trade_compliance_model.yaml"
    
    cortex_search_service: str = "EXCEPTION_SEARCH_SERVICE"
    cortex_model: str = "claude-3-5-sonnet"
    
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_prefix = "TC_"
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
