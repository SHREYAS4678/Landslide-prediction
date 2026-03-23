"""Alerts — create, list, resolve."""
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.db_models import Alert
from app.routers.auth import verify_token

router = APIRouter()

class AlertIn(BaseModel):
    region:     str
    risk_level: str
    message:    str
    sensors:    dict = Field(default_factory=dict)

@router.post("", status_code=201)
def create_alert(data: AlertIn, db: Session = Depends(get_db)):
    a = Alert(**data.model_dump())
    db.add(a); db.commit(); db.refresh(a)
    return {"id": a.id, "created_at": a.created_at}

@router.get("")
def list_alerts(
    active_only: bool = True,
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
    _: str = Depends(verify_token),
):
    q = db.query(Alert)
    if active_only:
        q = q.filter(Alert.resolved == False)
    rows = q.order_by(Alert.created_at.desc()).limit(limit).all()
    return [
        {
            "id": r.id, "region": r.region, "risk_level": r.risk_level,
            "message": r.message, "sensors": r.sensors,
            "resolved": r.resolved, "created_at": r.created_at,
        }
        for r in rows
    ]

@router.delete("/{alert_id}", status_code=204)
def resolve_alert(alert_id: int, db: Session = Depends(get_db), _: str = Depends(verify_token)):
    a = db.query(Alert).filter(Alert.id == alert_id).first()
    if a:
        a.resolved = True
        db.commit()
