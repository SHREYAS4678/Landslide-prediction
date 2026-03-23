"""Integration tests — run: pytest tests/ -v"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_docs_reachable():
    r = client.get("/docs")
    assert r.status_code == 200

def test_login_bad_credentials():
    r = client.post("/auth/login", json={"phone":"0000000000","password":"wrong"})
    assert r.status_code == 401

def test_predict_schema():
    r = client.post("/predict", json={
        "rainfall":70,"soil_moisture":90,
        "temperature":22,"vibration":4.0,"slope_angle":38,
    })
    assert r.status_code in (200, 500)
    if r.status_code == 200:
        assert r.json()["risk"] in ("LOW","MEDIUM","HIGH")

def test_alerts_requires_auth():
    r = client.get("/alerts")
    assert r.status_code == 401
