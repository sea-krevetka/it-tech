import os
from typing import Optional

class Settings:
    """Настройки приложения"""
    
    # Debug режим (включен только в разработке)
    DEBUG: bool = os.environ.get("DEBUG", "False").lower() == "true"
    
    # Порт приложения
    PORT: int = int(os.environ.get("PORT", 8283))
    
    # Секретный ключ (должен быть в переменных окружения!)
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "")
    
    # Database URL
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "")
    
    # JWT настройки
    JWT_SECRET: str = os.environ.get("JWT_SECRET", "")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60

settings = Settings()

# Проверка обязательных секретов
if not settings.SECRET_KEY and not settings.DEBUG:
    raise ValueError("SECRET_KEY environment variable is required in production!")