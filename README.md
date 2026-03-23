# LandSlide AI — Backend

Real-time landslide risk prediction using multi-sensor fusion + Random Forest / XGBoost ensemble.

## Stack
- **FastAPI** — REST API + WebSocket
- **PostgreSQL** — sensor data, users, alerts
- **scikit-learn + XGBoost** — ML prediction
- **Docker** — containerised deployment
- **Render / Railway** — cloud hosting

## Quick start (local)

```bash
# 1. Clone & install
git clone https://github.com/yourname/landslide-ai
cd landslide-ai
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. Start PostgreSQL (Docker)
docker-compose up db -d

# 3. Set environment
cp .env.example .env      # fill in DATABASE_URL + SECRET_KEY

# 4. Train ML model
python ml/train.py

# 5. Seed database
python scripts/seed_db.py

# 6. Run API
uvicorn app.main:app --reload
# → http://localhost:8000/docs
```

## Deploy to Render (free tier)

1. Push repo to GitHub
2. Go to https://render.com → New → Blueprint
3. Connect your repo — Render reads `render.yaml` automatically
4. Set `SECRET_KEY` in the Render dashboard env vars
5. Done — your API is live at `https://landslide-api.onrender.com`

Add deploy hook URL to GitHub secret `RENDER_DEPLOY_HOOK` for CI/CD.

## API endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/register` | No | Create account |
| POST | `/auth/login` | No | Get JWT token |
| GET | `/auth/me` | Yes | Current user |
| POST | `/sensors/data` | No | Ingest reading |
| GET | `/sensors/live/{region}` | No | Latest reading |
| GET | `/sensors/history` | Yes | Paginated history |
| GET | `/sensors/regions` | No | Known regions |
| POST | `/predict` | No | ML prediction |
| GET | `/alerts` | Yes | Active alerts |
| POST | `/alerts` | No | Create alert |
| DELETE | `/alerts/{id}` | Yes | Resolve alert |
| POST | `/pdf/extract` | No | Extract PDF thresholds |
| GET | `/admin/stats` | Yes | System stats |
| WS | `/ws/live/{region}` | No | Live sensor stream |
| GET | `/health` | No | Health check |

## Running tests

```bash
pytest tests/ -v
```

## Train model on your own data

Put a CSV at `data/landslide_sensor_data.csv` with columns:
`rainfall, soil_moisture, temperature, vibration, slope_angle, risk_label`

Then run `python ml/train.py`.
