from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Supabase
    supabase_url: str
    supabase_key: str
    supabase_service_key: str
    database_url: str
    
    # API Keys
    youtube_api_key: str
    discourse_api_key: str = ""
    discourse_api_username: str = ""
    
    # Application
    app_env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    
    # Scheduler
    enable_scheduler: bool = True
    cron_schedule: str = "0 2 * * *"
    
    # Rate Limiting
    youtube_requests_per_day: int = 9000
    discourse_requests_per_minute: int = 60
    
    # Data Collection
    workflows_per_platform: int = 20
    countries: str = "US,IN"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def country_list(self) -> List[str]:
        """Return countries as a list"""
        return [c.strip() for c in self.countries.split(",")]

settings = Settings()
