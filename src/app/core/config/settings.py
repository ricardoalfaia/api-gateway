from functools import lru_cache
from typing import Dict, Any
import yaml
import os
from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings

class ServiceConfig(BaseModel):
    url: str
    timeout: int = 30
    enabled: bool = True

class ServerConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000

class AppConfig(BaseModel):
    name: str
    version: str
    api_prefix: str

class CorsConfig(BaseModel):
    allow_origins: list[str]
    allow_methods: list[str]
    allow_headers: list[str]

class Settings(BaseSettings):
    app: AppConfig
    cors: CorsConfig
    server: ServerConfig
    services: Dict[str, ServiceConfig]

    @property
    def PROJECT_NAME(self) -> str:
        return self.app.name

    @property
    def API_V1_STR(self) -> str:
        return self.app.api_prefix

    @property
    def VERSION(self) -> str:
        return self.app.version

    @classmethod
    def load_config(cls) -> Dict[str, Any]:
        env = os.getenv("APP_ENV", "development")
        config_path = Path(__file__).parent / "environments"
        
        # Carrega configurações base
        with open(config_path / "base.yaml") as f:
            config = yaml.safe_load(f)
            
        # Carrega configurações do ambiente
        env_file = config_path / f"{env}.yaml"
        if env_file.exists():
            with open(env_file) as f:
                env_config = yaml.safe_load(f)
                config = deep_merge(config, env_config)
                
        return config

    class Config:
        case_sensitive = True

def deep_merge(base_dict: dict, update_dict: dict) -> dict:
    for key, value in update_dict.items():
        if isinstance(value, dict) and key in base_dict:
            base_dict[key] = deep_merge(base_dict[key], value)
        else:
            base_dict[key] = value
    return base_dict

@lru_cache()
def get_settings() -> Settings:
    config = Settings.load_config()
    return Settings(**config)

# Instância das configurações
settings = get_settings()