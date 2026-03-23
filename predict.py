"""ML prediction endpoint — calls the trained model."""
import os, joblib, numpy as np
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

MODEL_PATH  = Path(os.getenv("MODEL_PATH",  "ml/models/rf_model.pkl"))
SCALER_PATH = Path(os.getenv("SCALER_PATH", "ml/models/scaler.pkl"))

_model = _scaler = None

def _load():
    global _model, _scaler
    if _model is None:
        if not MODEL_PATH.exists():
            raise HTTPException(500, "Model not found. Run ml/train.py first.")
        _model  = joblib.load(MODEL_PATH)
        _scaler = joblib.load(SCALER_PATH)

LABELS = {0: "LOW", 1: "MEDIUM", 2: "HIGH"}

class PredictIn(BaseModel):
    rainfall:      float
    soil_moisture: float
    temperature:   float
    vibration:     float
    slope_angle:   float

class PredictOut(BaseModel):
    risk:           str
    score:          float
    confidence:     str
    probabilities:  dict

@router.post("", response_model=PredictOut)
def predict(data: PredictIn):
    """Run the Random Forest + XGBoost ensemble and return risk level."""
    _load()
    features = np.array([[
        data.rainfall,
        data.soil_moisture,
        data.temperature,
        data.vibration,
        data.slope_angle,
        data.soil_moisture * data.rainfall,              # engineered: soil×rain
        data.vibration * (data.slope_angle / 45.0),      # engineered: vib×slope
        100.0 - data.soil_moisture,                      # engineered: moisture deficit
    ]])
    scaled = _scaler.transform(features)
    pred   = int(_model.predict(scaled)[0])
    proba  = _model.predict_proba(scaled)[0].tolist()
    return PredictOut(
        risk=LABELS[pred],
        score=round(max(proba), 4),
        confidence=f"{max(proba)*100:.1f}%",
        probabilities={"LOW": round(proba[0],4), "MEDIUM": round(proba[1],4), "HIGH": round(proba[2],4)},
    )
