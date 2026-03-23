"""SQLAlchemy ORM models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Boolean, DateTime, Text, JSON, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone      = Column(String(15), unique=True, nullable=False, index=True)
    password   = Column(Text, nullable=False)
    role       = Column(String(20), default="operator")
    created_at = Column(DateTime, default=datetime.utcnow)

class SensorReading(Base):
    __tablename__ = "sensor_readings"
    id            = Column(BigInteger, primary_key=True, autoincrement=True)
    region        = Column(String(100), nullable=False, index=True)
    rainfall      = Column(Float, nullable=False)
    soil_moisture = Column(Float, nullable=False)
    temperature   = Column(Float, nullable=False)
    vibration     = Column(Float, nullable=False)
    slope_angle   = Column(Float, nullable=False)
    risk_level    = Column(String(10))
    risk_score    = Column(Float)
    recorded_at   = Column(DateTime, default=datetime.utcnow, index=True)

class Alert(Base):
    __tablename__ = "alerts"
    id         = Column(BigInteger, primary_key=True, autoincrement=True)
    region     = Column(String(100))
    risk_level = Column(String(10))
    message    = Column(Text)
    sensors    = Column(JSON)
    resolved   = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
