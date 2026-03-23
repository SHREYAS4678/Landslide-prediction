"""Admin — system stats (protected)."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.db_models import SensorReading, Alert, User
from app.routers.auth import verify_token

router = APIRouter()

@router.get("/stats")
def stats(db: Session = Depends(get_db), _: str = Depends(verify_token)):
    return {
        "total_readings": db.query(SensorReading).count(),
        "active_alerts":  db.query(Alert).filter(Alert.resolved == False).count(),
        "total_users":    db.query(User).count(),
        "regions":        db.query(SensorReading.region).distinct().count(),
    }
