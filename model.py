from database import Base 
from sqlalchemy import Column, Integer, String, Float, DateTime

class Violation(Base):
    __tablename__ = "violations" 
    id = Column(Integer, primary_key=True, index=True) 
    drone_id = Column(String, index=True, nullable=False)     
    timestamp = Column(DateTime, nullable=False)
    position_x = Column(Float, nullable=False) 
    position_y = Column(Float, nullable=False)
    position_z = Column(Float, nullable=False)
    owner_first_name = Column(String, nullable=False) 
    owner_last_name = Column(String, nullable=False)
    owner_ssn = Column(String, nullable=False)
    owner_phone = Column(String, nullable=False)