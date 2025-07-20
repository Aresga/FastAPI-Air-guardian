from src.database import Base
from sqlalchemy import Column, Integer, String, Float, DateTime

"""
SQLAlchemy ORM model for the 'violations' table.

Represents a drone violation event, including drone and owner details, 
violation timestamp, and 3D position.

Attributes:
	index (int): Primary key for the violation record.
	id (str): Unique identifier for the violation.
	drone_id (str): Identifier for the drone involved in the violation.
	timestamp (datetime): Date and time when the violation occurred.
	position_x (float): X coordinate of the drone's position.
	position_y (float): Y coordinate of the drone's position.
	position_z (float): Z coordinate of the drone's position.
	owner_first_name (str): First name of the drone's owner.
	owner_last_name (str): Last name of the drone's owner.
	owner_ssn (str): Social security number of the drone's owner.
	owner_phone (str): Phone number of the drone's owner.
"""

class Violation(Base):
    __tablename__ = "violations" 
    index = Column(Integer, primary_key=True, index=True) 
    id = Column(String, index=True, nullable=False)     
    drone_id = Column(String, index=True, nullable=False)     
    timestamp = Column(DateTime, nullable=False)
    position_x = Column(Float, nullable=False) 
    position_y = Column(Float, nullable=False)
    position_z = Column(Float, nullable=False)
    owner_first_name = Column(String, nullable=False) 
    owner_last_name = Column(String, nullable=False)
    owner_ssn = Column(String, nullable=False)
    owner_phone = Column(String, nullable=False)