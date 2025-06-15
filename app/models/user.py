from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean
from app.db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    profile_picture = Column(String(255))
    designation = Column(String(255))
    birthdate = Column(DateTime)
    join_date = Column(DateTime)
    mood_score = Column(Float)
    predicted_burnout_risk = Column(Boolean)