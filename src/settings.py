from pydantic_settings import BaseSettings, SettingsConfigDict
import os

"""
This module defines application settings using Pydantic's BaseSettings for environment-based configuration.

Classes:
	Settings: Loads configuration from .env file. 
		- NFZ_SECRET_KEY (str): Secret key for No-Fly Zone operations end point. 
		- BASE_URL (str): Base URL for the drones APIA.
		- DATABASE_URL (str): Database connection string.
		- CELERY_BROKER_URL (str): URL for the Celery message broker (redis).
Exceptions:
	Raises a RuntimeError if the .env file is missing or if there is an error loading environment variables.
"""
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    NFZ_SECRET_KEY: str
    BASE_URL: str
    DATABASE_URL: str
    CELERY_BROKER_URL: str

try:
    settings = Settings()
except Exception as e:
    if not os.path.exists('.env'):
        raise RuntimeError(".env file not found. Please create a .env file with the required environment variables.") from e
    else:
        raise RuntimeError(f"Error loading environment variables: {e}") from e