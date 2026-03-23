"""Authentication — login with phone + password, returns JWT."""
import os
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from app.database import get_db
from app.models.db_models import User

router = APIRouter()
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login")

SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production-use-32-chars-min")
ALGORITHM  = "HS256"
TOKEN_EXP  = int(os.getenv("TOKEN_EXPIRE_HOURS", "24"))

class LoginRequest(BaseModel):
    phone:    str
    password: str

class RegisterRequest(BaseModel):
    phone:    str
    password: str
    role:     str = "operator"

def create_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(hours=TOKEN_EXP)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str = Depends(oauth2)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        phone: str = payload.get("sub")
        if not phone:
            raise HTTPException(status_code=401, detail="Invalid token")
        return phone
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@router.post("/register", status_code=201)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.phone == req.phone).first():
        raise HTTPException(status_code=409, detail="Phone already registered")
    user = User(phone=req.phone, password=pwd_ctx.hash(req.password), role=req.role)
    db.add(user); db.commit()
    return {"message": "User created", "phone": req.phone}

@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == req.phone).first()
    if not user or not pwd_ctx.verify(req.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token({"sub": user.phone, "role": user.role})
    return {"access_token": token, "token_type": "bearer", "role": user.role}

@router.get("/me")
def me(phone: str = Depends(verify_token), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == phone).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"phone": user.phone, "role": user.role, "created_at": user.created_at}
