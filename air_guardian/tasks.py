import httpx
import math
from datetime import datetime

from celery_app import celery
from database import SessionLocal
from models import Violation
from settings import settings

# [cite_start]The No-Fly Zone is a circle with a radius of 1000 units[cite: 69].
NFZ_RADIUS = 1000.0

@celery.task
def check_for_violations():
    """
    A periodic task that fetches drone data, checks for NFZ violations,
    and stores them in the database.
    """
    print(f"[{datetime.utcnow()}] Running violation check...")

    try:
        # Step 1: Fetch all current drone positions
        drones_response = httpx.get(settings.DRONES_API_URL)
        drones_response.raise_for_status() # Raise an exception for bad status codes
        drones = drones_response.json()

        violators = []
        for drone in drones:
            x, y = drone['positionX'], drone['positionY']
            
            # Step 2: Calculate distance from the center (0,0) and check for violation
            # [cite_start]The z-coordinate is not used for NFZ detection[cite: 66].
            distance = math.sqrt(x**2 + y**2)

            if distance <= NFZ_RADIUS:
                print(f"Violation detected! Drone ID: {drone['id']}, Distance: {distance:.2f}")
                
                # Step 3: Fetch owner information for the violating drone
                owner_url = f"https://drones-api.hive.fi/users/{drone['owner_id']}"
                owner_response = httpx.get(owner_url)
                
                if owner_response.status_code == 200:
                    owner_info = owner_response.json()
                    
                    # Prepare the violation record
                    new_violation = {
                        "drone_id": drone['id'],
                        "timestamp": datetime.utcnow(),
                        "position_x": x,
                        "position_y": y,
                        "position_z": drone['positionZ'],
                        "owner_first_name": owner_info['firstName'],
                        "owner_last_name": owner_info['lastName'],
                        "owner_ssn": owner_info['ssn'],
                        "owner_phone": owner_info['phoneNumber']
                    }
                    violators.append(new_violation)
                else:
                    print(f"Warning: Could not fetch owner info for drone {drone['id']}")

        # Step 4: Store all detected violations in the database
        if violators:
            # We need to use a database session to talk to the database
            with SessionLocal() as db:
                for v_data in violators:
                    db_violation = Violation(**v_data)
                    db.add(db_violation)
                db.commit()
            print(f"Successfully stored {len(violators)} new violation(s) in the database.")

    except httpx.RequestError as exc:
        print(f"Error fetching drone data: {exc}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")