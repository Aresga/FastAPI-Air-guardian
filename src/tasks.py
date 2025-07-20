import asyncio
import httpx
import math
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import logging
import src.schemas as schemas
import src.errors as Errors
from pydantic import ValidationError

from src.celery_app import celery
from src.model import Violation
from src.settings import settings


"""
This module defines Celery tasks and helper functions for detecting and recording drone violations
of a no-fly zone (NFZ) in a FastAPI application. It periodically fetches drone positions from an
external API, checks if any drones have entered the NFZ, and records violations in the database.
To prevent duplicate entries, recent violators are cached and only re-logged after a cooldown period.
Functions:
	save_violations_to_db(violations_data: list):
		Asynchronously saves a list of violation records to the database using SQLAlchemy async engine.
	check_for_violations():
		Celery task that:
			- Fetches current drone positions from an external API.
			- Checks if any drones are within the NFZ radius.
			- Fetches owner information for violating drones.
			- Records new violations in the database, avoiding duplicates using a cooldown cache.
			- Handles and logs errors related to API requests and database operations.
Globals:
	RECENT_VIOLATORS (dict): Cache mapping drone owner IDs to the timestamp of their last violation.
	VIOLATION_COOLDOWN (timedelta): Time period before a violator can be recorded again.
	NFZ_RADIUS (float): Radius of the no-fly zone in meters.
Logging:
	Logs all major actions, errors, and warnings to both a file and the console.
"""


RECENT_VIOLATORS = {} # -> drone_id + timestamp
VIOLATION_COOLDOWN = timedelta(seconds=120)
NFZ_RADIUS = 1000.0

# Configure logging for Celery tasks
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/celery_worker.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def save_violations_to_db(violations_data: list):
    """ Creates DB connection, saves violations, and closes it """
    try:
        engine = create_async_engine(settings.DATABASE_URL)
        SessionLocal = async_sessionmaker(bind=engine)

        async with SessionLocal() as db:
            for v_data in violations_data:
                db_violation = Violation(**v_data)
                db.add(db_violation)
            await db.commit()

        logger.info(f"Successfully stored {len(violations_data)} new violation(s) in the database.")
        await engine.dispose() ## <<-- close the engine connection
    except Exception as e:
        logger.error(f"Database error: {e}")
        logger.debug(f"Database URL: {settings.DATABASE_URL}")
        raise


@celery.task
def check_for_violations():
    now = datetime.now()
    logger.info(f"Starting violation check at {now}")

    # Clean up old violators from the cache to allow re-logging after cooldown
    for drone_id, timestamp in list(RECENT_VIOLATORS.items()):
        if now > timestamp + VIOLATION_COOLDOWN:
            del RECENT_VIOLATORS[drone_id]


    try:
        # Fetch all current drone positions from the external API
        with httpx.Client(timeout=10.0) as client:
            logger.info("Fetching drone data from external API")
            drones_response = client.get(settings.BASE_URL + "drones")
            drones_response.raise_for_status()
            drones = drones_response.json()
            
        # Validate data format
        if not isinstance(drones, list):
            logger.error("Invalid drone data format: expected list")
            return "Error: Invalid data format from drone API"
            
        logger.info(f"Successfully fetched {len(drones)} drones")

        new_violators_to_save = []

        # main loop for checking each drone for NFZ violations
        for drone in drones:
            try:
                if drone['owner_id'] in RECENT_VIOLATORS:
                    continue 
                
                # Using Pythagorean theorem to calculate distance from origin (0,0)
                x, y = drone['x'], drone['y']
                distance = math.sqrt(x**2 + y**2)

                if distance <= NFZ_RADIUS:
                    time_now = datetime.now()
                    logger.warning(f"Violation detected! Drone ID: {drone['owner_id']}, Distance: {distance:.2f}")
                    with httpx.Client(timeout=10.0) as client:
                        owner_data = client.get(settings.BASE_URL + "users/" + str(drone['owner_id']))
                    
                    if owner_data.status_code == 200:
                        owner_info = owner_data.json()
                        if not isinstance(owner_info, dict):
                            logger.error("Invalid owner data format: expected dict")
                            return "Error: Invalid data format from users API"

                        # Prepare the violation record
                        new_violation = {
                            "id": str(drone['owner_id']),
                            "drone_id": drone['id'],
                            "timestamp": time_now,
                            "position_x": x,
                            "position_y": y,
                            "position_z": drone['z'],
                            "owner_first_name": owner_info['first_name'],
                            "owner_last_name": owner_info['last_name'],
                            "owner_ssn": owner_info['social_security_number'],
                            "owner_phone": owner_info['phone_number']
                        }
                        new_violators_to_save.append(new_violation)
                        # Add the new violator to our cache
                        RECENT_VIOLATORS[drone['owner_id']] = now
                        logger.info(f"Violation recorded for drone {drone['owner_id']}")
                    else:
                        logger.warning(f"Could not fetch owner info for drone {drone['owner_id']}: HTTP {owner_data.status_code}")
                        

            except (ValueError, TypeError, KeyError) as e:
                logger.error(f"Data validation error for drone {drone.get('owner_id', 'unknown')}: {e}")
                continue

        if new_violators_to_save:
            asyncio.run(save_violations_to_db(new_violators_to_save))
            logger.info(f"Saved {len(new_violators_to_save)} violations to database")
        else:
            logger.info("No new violations detected")


    except httpx.TimeoutException:
        logger.error("Timeout while fetching data from external API")
        return "Error: API timeout"
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error from external API: {e.response.status_code}")
        return f"Error: External API HTTP {e.response.status_code}"
    except httpx.RequestError as e:
        logger.error(f"Network error connecting to external API: {e}")
        return "Error: Network connection failed"
    except Exception as e:
        logger.error(f"Unexpected error in violation check: {e}")
        return f"Error: {str(e)}"

    return "Violation check complete."
