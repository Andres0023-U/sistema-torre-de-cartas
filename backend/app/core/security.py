import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.core.database import get_db

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("Falta la variable de entorno SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

bearer_scheme = HTTPBearer()

def get_current_user_payload(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    from app.models.security import User  # import local para evitar ciclos
    user = db.query(User).filter(User.user_id == int(payload["sub"])).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Cuenta desactivada o inexistente")

    return payload

def require_role(allowed_roles: list[str]):
    def role_checker(payload: dict = Depends(get_current_user_payload)):
        if payload.get("role") not in allowed_roles:
            raise HTTPException(status_code=403, detail="No tienes permiso para esta acción")
        return payload
    return role_checker

MANAGER_ROLES = ["organizer", "admin"]


def can_manage_tournament(payload: dict, tournament) -> bool:
    # El admin gestiona cualquier torneo; el organizador solo los suyos
    return payload.get("role") == "admin" or tournament.organizer_id == int(payload["sub"])