from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.schemas.auth import LoginRequest, TokenResponse
from app.models.security import User, Role
from app.core.security import verify_password, create_access_token, get_current_user_payload

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    role = db.query(Role).filter(Role.role_id == user.role_id).first()

    token = create_access_token({"sub": str(user.user_id), "role": role.name})

    return TokenResponse(access_token=token, role=role.name)

@router.get("/me")
def read_current_user(payload: dict = Depends(get_current_user_payload)):
    return {"user_id": payload.get("sub"), "role": payload.get("role")}