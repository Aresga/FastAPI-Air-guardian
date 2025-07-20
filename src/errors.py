import httpx
from fastapi import HTTPException
from src.settings import settings
import logging

"""
Module for centralized error handling and logging.
This module provides the `Errors` class with static methods to handle and log
various exceptions that may occur during HTTP requests to external APIs, as well
as data validation errors.
Classes:
    Errors: Contains static methods for handling httpx exceptions and validation errors.
Methods:
    handle_httpx_error(e):
        Handles exceptions raised by httpx during API calls, logs the error, and raises
        appropriate FastAPI HTTPException with relevant status codes and messages.
    handle_validation_error(e):
        Handles data validation errors, logs the error, and raises a FastAPI HTTPException
        indicating invalid data from the external API.
Logging:
    Configures logging to output to both a file ("logs/fastapi.log") and the console,
    including timestamps, logger name, log level, and message.
"""


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("logs/fastapi.log"),
                        logging.StreamHandler()]
                    )
logger = logging.getLogger(__name__)

class Errors(Exception):
    @staticmethod
    def handle_httpx_error(e):
        if isinstance(e, httpx.TimeoutException):
            logger.error("Timeout while fetching drone data")
            raise HTTPException(status_code=504, detail="Gateway timeout: External API took too long to respond")
        elif isinstance(e, httpx.HTTPStatusError):
            logger.error(f"HTTP error from external API: {e.response.status_code}")
            if e.response.status_code == 404:
                raise HTTPException(status_code=404, detail="Drone data not found")
            elif e.response.status_code >= 500:
                raise HTTPException(status_code=502, detail="External API server error")
            else:
                raise HTTPException(status_code=e.response.status_code, detail=f"External API error: {str(e)}")
        elif isinstance(e, httpx.RequestError):
            logger.error(f"Network error connecting to drones API: {str(e)}")
            raise HTTPException(status_code=503, detail="Service unavailable: Cannot connect to drone API")
        else:
            logger.error(f"Unexpected error in get_drones: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    @staticmethod
    def handle_validation_error(e):
        logger.error(f"Invalid drone data: {e}")
        raise HTTPException(status_code=502, detail="Invalid data from external API") 
    