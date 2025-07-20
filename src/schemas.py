from pydantic import BaseModel
from datetime import datetime

"""
Pydantic model used for data validation of violation records,
when interacting with API endpoints and the database.
Each violation contains information about the drone involved, the time
and location of the violation, and the owner's personal details.
Attributes:
	index (int): The index or sequence number of the violation.
	id (str): Unique identifier for the violation.
	drone_id (str): Identifier of the drone involved in the violation.
	timestamp (datetime): The date and time when the violation occurred.
	position_x (float): X-coordinate of the drone's position at the time of violation.
	position_y (float): Y-coordinate of the drone's position at the time of violation.
	position_z (float): Z-coordinate (altitude) of the drone's position at the time of violation.
	owner_first_name (str): First name of the drone's owner.
	owner_last_name (str): Last name of the drone's owner.
	owner_ssn (str): Social Security Number of the drone's owner.
	owner_phone (str): Phone number of the drone's owner.
Config:
	from_attributes (bool): Enables population of the model from ORM objects SQLAlchemy models.
"""
class Violation(BaseModel):
    index: int
    id: str
    drone_id: str
    timestamp: datetime
    position_x: float
    position_y: float
    position_z: float
    owner_first_name: str
    owner_last_name: str
    owner_ssn: str
    owner_phone: str

    """ inherit attributes from the SQLAlchemy model """
    class Config:
        from_attributes = True


class Drone(BaseModel):
	id: str
	owner_id: int
	x: int
	y: int
	z: int

	class Config:
		from_attributes = True
            
class Owner_data(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone_number: str
    social_security_number: str
    purchased_at: datetime

    class Config:
        from_attributes = True
