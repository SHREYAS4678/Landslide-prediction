"""Sensor data — ingest, retrieve, history."""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.db_models import SensorReading
from app.routers.auth import verify_token

router = APIRouter()

class SensorIn(BaseModel):
    region:        str
    rainfall:      float
    soil_moisture: float
    temperature:   float
    vibration:     float
    slope_angle:   float
    risk_level:    Optional[str] = None
    risk_score:    Optional[float] = None

@router.post("/data", status_code=201)
def ingest(data: SensorIn, db: Session = Depends(get_db)):
    """Ingest one sensor reading. Call from IoT device or simulator."""
    row = SensorReading(**data.model_dump())
    db.add(row); db.commit(); db.refresh(row)
    return {"id": row.id, "recorded_at": row.recorded_at}

@router.get("/live/{region}")
def live(region: str, db: Session = Depends(get_db)):
    """Latest sensor reading for a region."""
    row = (
        db.query(SensorReading)
        .filter(SensorReading.region == region)
        .order_by(SensorReading.recorded_at.desc())
        .first()
    )
    if not row:
        return {"region": region, "data": None}
    return {
        "region": row.region,
        "rainfall": row.rainfall,
        "soil_moisture": row.soil_moisture,
        "temperature": row.temperature,
        "vibration": row.vibration,
        "slope_angle": row.slope_angle,
        "risk_level": row.risk_level,
        "risk_score": row.risk_score,
        "recorded_at": row.recorded_at,
    }

@router.get("/history")
def history(
    region: str,
    limit:  int = Query(50, le=500),
    offset: int = 0,
    db: Session = Depends(get_db),
    _: str = Depends(verify_token),
):
    """Paginated history for charts and analysis."""
    rows = (
        db.query(SensorReading)
        .filter(SensorReading.region == region)
        .order_by(SensorReading.recorded_at.desc())
        .offset(offset).limit(limit).all()
    )
    return [
        {
            "id": r.id, "rainfall": r.rainfall, "soil_moisture": r.soil_moisture,
            "temperature": r.temperature, "vibration": r.vibration,
            "slope_angle": r.slope_angle, "risk_level": r.risk_level,
            "risk_score": r.risk_score, "recorded_at": r.recorded_at,
        }
        for r in rows
    ]

@router.get("/regions")
def list_regions(db: Session = Depends(get_db)):
    """Distinct regions that have sensor data."""
    rows = db.query(SensorReading.region).distinct().all()
    return [r[0] for r in rows]
