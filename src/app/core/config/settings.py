from functools import lru_cache
from typing import Dict, Any, List
import yaml
import os
import logging
from pathlib import Path
from pydantic import BaseModel, field_validator
from pydantic_settings import BaseSettings

class MTLSSettings(BaseModel):
    enabled: bool = False
    cert_path: str = "certs/client.crt"
    key_path: str = "certs/client.key"
    ca_path: str = "certs/ca.crt"

class PerformanceConfig(BaseModel):
    debug_mode: bool = False
    enable_timing_middleware: bool = True
    log_slow_requests: bool = True
    slow_request_threshold: float = 1.0  

class ServiceConfig(BaseModel):
    url: str
    timeout: int = 30
    enabled: bool = True
    api_key: str | None = None
    require_mtls: bool = False

    @field_validator('timeout')
    def timeout_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('timeout must be positive')
        return v    
class Config:
    case_sensitive = True    
    from_attributes = True
    
class AppConfig(BaseModel):
    name: str
    version: str
    api_prefix: str

class ServerConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000

class CorsConfig(BaseModel):
    allow_origins: List[str]
    allow_methods: List[str]
    allow_headers: List[str]

class LoggingConfig(BaseModel):
    level: str = "INFO"
    format: str = "%(asctime)s - %(levelname)s - %(message)s"
class InternalNetworkConfig(BaseModel):
    ranges: List[str]

class Settings(BaseSettings):
    app: AppConfig
    cors: CorsConfig
    server: ServerConfig
    logging: LoggingConfig
    services: Dict[str, ServiceConfig]
    internal_network: InternalNetworkConfig   
    # Suas configurações existentes...
    api_keys: List[str] = []
    mtls: MTLSSettings
    performance: PerformanceConfig = PerformanceConfig() 
    
    @property
    def PROJECT_NAME(self) -> str:
        return self.app.name

    @property
    def API_V1_STR(self) -> str:
        return self.app.api_prefix

    @property
    def VERSION(self) -> str:
        return self.app.version

    def configure_logging(self):
        """Configure logging based on settings"""
        logging.basicConfig(
            level=getattr(logging, self.logging.level.upper()),
            format=self.logging.format
        )

    # @classmethod
    # def load_config(cls) -> Dict[str, Any]:
    #     env = os.environ.get("APP_ENV", "development")
    #     if env != "production":
    #         env = "development"
        
    #     logging.info(f"Loading configuration for environment: {env}")
    #     config_path = Path(__file__).parent / "environments"
        
    #     try:
    #         with open(config_path / "base.yaml") as f:
    #             config = yaml.safe_load(f)
                
    #         env_file = config_path / f"{env}.yaml"
    #         if env_file.exists():
    #             with open(env_file) as f:
    #                 env_config = yaml.safe_load(f)
    #                 if env_config:
    #                     config = deep_merge(config, env_config)
    #                     logging.info(f"Loaded environment config: {env_config}")
    #         return config
    #     except yaml.YAMLError as e:
    #         logging.error(f"Error loading YAML configuration: {e}")
    #         raise
    #     except Exception as e:
    #         logging.error(f"Unexpected error loading configuration: {e}")
    #         raise



    @classmethod
    def load_config(cls) -> Dict[str, Any]:
        # Forçar o ambiente como development se não estiver explicitamente definido como production
        env = os.environ.get("APP_ENV", "development")
        if env != "production":
            env = "development"
        
        logging.info(f"Loading configuration for environment: {env}")
        config_path = Path(__file__).parent / "environments"
        
        # Carrega configurações base
        with open(config_path / "base.yaml") as f:
            config = yaml.safe_load(f)
            
        # Carrega configurações do ambiente
        env_file = config_path / f"{env}.yaml"
        if env_file.exists():
            with open(env_file) as f:
                env_config = yaml.safe_load(f)
                if env_config:
                    config = deep_merge(config, env_config)
                    logging.info(f"Loaded environment config: {env_config}")
                
        return config

    

def deep_merge(base_dict: dict, update_dict: dict) -> dict:
    """Merge recursivamente dois dicionários."""
    if not isinstance(base_dict, dict) or not isinstance(update_dict, dict):
        return update_dict

    merged = base_dict.copy()
    
    for key, value in update_dict.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
            
    return merged

def get_settings() -> Settings:
    config = Settings.load_config()
    settings = Settings(**config)
    logging.debug(f"Loaded services configuration: {settings.services}")
    return settings

# Instância das configurações
settings = get_settings()