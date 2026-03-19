from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    phone_number: str
    password: str

class UserResponse(BaseModel):
    id: str
    phone_number: str
    created_at: datetime

class UserInDB(UserCreate):
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SensorData(BaseModel):
    soil_moisture: float
    rainfall: float
    temperature: float
    vibration: float
    tilt: float
    humidity: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class PredictionResponse(BaseModel):
    risk_score: float
    risk_level: str
    timestamp: datetime
