"""
Configuration settings for the application
Optimized for Pydantic Settings v2
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from dotenv import load_dotenv

# Load .env file explicitly
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"[CONFIG] Loaded .env from: {env_path}")
else:
    print(f"[CONFIG] .env not found at: {env_path}")


class Settings(BaseSettings):
    """Application settings with Pydantic Settings v2"""
    
    # Database - SQLite by default for easy setup
    DATABASE_URL: str = "sqlite:///./email_sender.db"
    
    # JWT Configuration
    SECRET_KEY: str = "your-secret-key-change-in-production-abc123xyz789"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24
    
    # SMTP Configuration
    SMTP_HOST: str = "mail.tablesa.com.co"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""  # Sender email address (defaults to SMTP_USER)
    SMTP_FROM_NAME: str = "Sistema de Correos"
    SMTP_SECURITY: str = "STARTTLS"  # STARTTLS, SSL, or NONE
    SMTP_TIMEOUT: int = 30  # Connection timeout in seconds
    
    # Admin Credentials
    ADMIN_USER: str = "Admin1"
    ADMIN_PASSWORD: str = "Admin123"
    
    # App Settings
    APP_NAME: str = "Sistema de Envio de Correos"
    DEBUG: bool = True
    
    # Email Settings
    EMAIL_DELAY_SECONDS: float = 2.0  # Delay between emails to avoid spam
    EMAIL_BATCH_SIZE: int = 50  # Number of emails before reconnecting
    
    # Pydantic Settings v2 configuration
    model_config = SettingsConfigDict(
        env_file=[".env", "../.env", "../../.env"],
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",  # Allow extra fields from .env
        env_ignore_empty=False,
    )
    
    @property
    def smtp_from_email(self) -> str:
        """Get the sender email address"""
        return self.SMTP_FROM if self.SMTP_FROM else self.SMTP_USER


def get_settings() -> Settings:
    """Get settings instance (no cache to ensure fresh values from .env)"""
    return Settings()


# Global settings instance - create after dotenv loads
settings = Settings()

# Debug: Print loaded values
print(f"[CONFIG] SMTP_HOST: {settings.SMTP_HOST}")
print(f"[CONFIG] SMTP_USER: {settings.SMTP_USER}")
print(f"[CONFIG] SMTP_FROM: {settings.SMTP_FROM}")
