from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from typing import List
import json
import asyncio
from app.models import UserCreate, UserResponse, SensorData, PredictionResponse
from app.ml_model import predictor
from datetime import datetime

router = APIRouter()

# Store active web socket connections
active_connections: List[WebSocket] = []

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate):
    # Mock registration (In a real app, hash password and save to DB)
    return UserResponse(
        id="mock_id_123",
        phone_number=user.phone_number,
        created_at=datetime.utcnow()
    )

@router.post("/login")
async def login(user: UserCreate):
    # Mock login
    if user.phone_number and user.password:
        return {"access_token": "mock_token", "token_type": "bearer"}
    raise HTTPException(status_code=400, detail="Invalid credentials")

@router.post("/sensor-data", response_model=PredictionResponse)
async def ingest_sensor_data(data: SensorData):
    # Predict risk
    features = [
        data.soil_moisture,
        data.rainfall,
        data.temperature,
        data.vibration,
        data.tilt,
        data.humidity
    ]
    risk_score = predictor.predict_risk(features)
    risk_level = predictor.determine_risk_level(risk_score)
    
    response = PredictionResponse(
        risk_score=risk_score,
        risk_level=risk_level,
        timestamp=datetime.utcnow()
    )

    # Broadcast to websockets
    broadcast_data = {
        "sensor_data": data.dict(),
        "prediction": response.dict()
    }
    await broadcast(json.dumps(broadcast_data, default=str))

    return response

async def broadcast(message: str):
    for connection in active_connections:
        try:
            await connection.send_text(message)
        except WebSocketDisconnect:
            active_connections.remove(connection)

@router.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            # Keep connection open, client just listens
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)
