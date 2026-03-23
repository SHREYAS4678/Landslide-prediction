"""Seed script — creates admin user + 100 sample readings."""
import sys, os, random, datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app.database import SessionLocal
from app.models.db_models import User, SensorReading, Alert
from passlib.context import CryptContext

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
db  = SessionLocal()

if not db.query(User).filter(User.phone == "9876543210").first():
    db.add(User(phone="9876543210", password=pwd.hash("password123"), role="admin"))
    print("Admin: 9876543210 / password123")

regions = ["munnar","darjeeling","shimla","ooty","coorg"]
now = datetime.datetime.utcnow()
for i in range(100):
    db.add(SensorReading(
        region=random.choice(regions),
        rainfall=round(random.uniform(0,100),1),
        soil_moisture=round(random.uniform(20,100),1),
        temperature=round(random.uniform(10,40),1),
        vibration=round(random.uniform(0,8),2),
        slope_angle=round(random.uniform(15,55),1),
        risk_level=random.choice(["LOW","MEDIUM","HIGH"]),
        risk_score=round(random.random(),3),
        recorded_at=now - datetime.timedelta(minutes=i*5),
    ))

db.add(Alert(region="munnar",risk_level="HIGH",
    message="Rainfall exceeded 50mm/hr. Soil saturation critical.",
    sensors={"rainfall":68,"soil_moisture":91,"vibration":4.2}))
db.commit(); db.close()
print("Seed complete.")
