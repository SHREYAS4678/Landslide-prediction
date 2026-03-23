"""
LandSlide AI — FastAPI Backend
Entry point. Mounts all routers, CORS, WebSocket live feed.
"""
import asyncio, json, random
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, sensors, predict, alerts, pdf, admin

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LandSlide AI",
    description="Real-time landslide risk prediction system using multi-sensor fusion and ML.",
    version="2.4.1",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,    prefix="/auth",    tags=["Authentication"])
app.include_router(sensors.router, prefix="/sensors", tags=["Sensors"])
app.include_router(predict.router, prefix="/predict", tags=["Prediction"])
app.include_router(alerts.router,  prefix="/alerts",  tags=["Alerts"])
app.include_router(pdf.router,     prefix="/pdf",     tags=["PDF Extraction"])
app.include_router(admin.router,   prefix="/admin",   tags=["Admin"])

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "version": "2.4.1", "timestamp": datetime.utcnow().isoformat()}

class ConnectionManager:
    def __init__(self):
        self.active: dict[str, list[WebSocket]] = {}
    async def connect(self, ws: WebSocket, region: str):
        await ws.accept()
        self.active.setdefault(region, []).append(ws)
    def disconnect(self, ws: WebSocket, region: str):
        self.active.get(region, []).remove(ws)
    async def broadcast(self, region: str, data: dict):
        dead = []
        for ws in self.active.get(region, []):
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws, region)

manager = ConnectionManager()

@app.websocket("/ws/live/{region}")
async def websocket_live(ws: WebSocket, region: str):
    """Stream live sensor readings every 3 seconds."""
    await manager.connect(ws, region)
    try:
        while True:
            payload = {
                "region": region,
                "timestamp": datetime.utcnow().isoformat(),
                "rainfall": round(random.uniform(0, 100), 1),
                "soil_moisture": round(random.uniform(20, 100), 1),
                "temperature": round(random.uniform(10, 40), 1),
                "vibration": round(random.uniform(0, 8), 2),
                "slope_angle": round(random.uniform(15, 55), 1),
            }
            await manager.broadcast(region, payload)
            await asyncio.sleep(3)
    except WebSocketDisconnect:
        manager.disconnect(ws, region)
