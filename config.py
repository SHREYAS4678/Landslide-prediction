"""Central config — reads from environment variables."""
import os

DATABASE_URL        = os.getenv("DATABASE_URL", "postgresql://postgres:changeme@localhost:5432/landslide_db").replace("postgres://","postgresql://",1)
SECRET_KEY          = os.getenv("SECRET_KEY", "change-me-in-production")
TOKEN_EXPIRE_HOURS  = int(os.getenv("TOKEN_EXPIRE_HOURS", "24"))
MODEL_PATH          = os.getenv("MODEL_PATH",  "ml/models/rf_model.pkl")
SCALER_PATH         = os.getenv("SCALER_PATH", "ml/models/scaler.pkl")
LOG_LEVEL           = os.getenv("LOG_LEVEL", "info")
ALERT_THRESHOLD     = float(os.getenv("ALERT_THRESHOLD", "0.70"))
