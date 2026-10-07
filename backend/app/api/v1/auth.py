from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.models.security import User, Role
from app.core.security import verify_password, hash_password, create_access_token, get_current_user_payload, require_role
from app.schemas.register import RegisterRequest
from app.schemas.user_admin import AssignRoleRequest, UserAdminResponse, UserListItem, SetActiveRequest, UpdateNameRequest
from app.models.players import Player

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Tu cuenta está desactivada. Contacta a un administrador.")

    role = db.query(Role).filter(Role.role_id == user.role_id).first()

    token = create_access_token({"sub": str(user.user_id), "role": role.name})

    return TokenResponse(access_token=token, role=role.name)

@router.get("/me")
def read_current_user(
    payload: dict = Depends(get_current_user_payload),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.user_id == int(payload["sub"])).first()
    return {
        "user_id": payload.get("sub"),
        "role": payload.get("role"),
        "name": user.name if user else None
    }

@router.post("/register", response_model=TokenResponse)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ese correo ya está registrado")

    pending_role = db.query(Role).filter(Role.name == "pending").first()
    if not pending_role:
        raise HTTPException(status_code=500, detail="Rol 'pending' no configurado en el sistema")

    new_user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        role_id=pending_role.role_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token({"sub": str(new_user.user_id), "role": pending_role.name})

    return TokenResponse(access_token=token, role=pending_role.name)


@router.get("/pending-users", response_model=list[UserAdminResponse])
def list_pending_users(
    db: Session = Depends(get_db),
    payload: dict = Depends(require_role(["admin"]))
):
    pending_role = db.query(Role).filter(Role.name == "pending").first()
    users = db.query(User).filter(User.role_id == pending_role.role_id).all()
    return [
        UserAdminResponse(user_id=u.user_id, name=u.name, email=u.email, role="pending")
        for u in users
    ]

@router.put("/users/{user_id}/role", response_model=UserAdminResponse)
def assign_role(
    user_id: int,
    data: AssignRoleRequest,
    db: Session = Depends(get_db),
    payload: dict = Depends(require_role(["admin"]))
):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    current_role = db.query(Role).filter(Role.role_id == user.role_id).first()
    if current_role.name != "pending":
        raise HTTPException(status_code=400, detail="Solo se puede asignar rol a usuarios pendientes")

    role = db.query(Role).filter(Role.name == data.role).first()
    if not role:
        raise HTTPException(status_code=500, detail=f"Rol '{data.role}' no configurado en el sistema")

    user.role_id = role.role_id

    # Los jugadores necesitan perfil para crear mazos e inscribirse
    if role.name == "player":
        has_profile = db.query(Player).filter(Player.user_id == user.user_id).first()
        if not has_profile:
            db.add(Player(user_id=user.user_id))

    db.commit()
    db.refresh(user)

    return UserAdminResponse(user_id=user.user_id, name=user.name, email=user.email, role=role.name)

@router.get("/users", response_model=list[UserListItem])
def list_users(
    db: Session = Depends(get_db),
    payload: dict = Depends(require_role(["admin"]))
):
    rows = (
        db.query(User, Role)
        .join(Role, Role.role_id == User.role_id)
        .order_by(User.user_id.asc())
        .all()
    )
    return [
        UserListItem(user_id=u.user_id, name=u.name, email=u.email, role=r.name, is_active=u.is_active)
        for u, r in rows
    ]


@router.put("/users/{user_id}/active", response_model=UserListItem)
def set_user_active(
    user_id: int,
    data: SetActiveRequest,
    db: Session = Depends(get_db),
    payload: dict = Depends(require_role(["admin"]))
):
    if user_id == int(payload["sub"]) and not data.is_active:
        raise HTTPException(status_code=400, detail="No puedes desactivar tu propia cuenta")

    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    user.is_active = data.is_active
    db.commit()
    db.refresh(user)

    role = db.query(Role).filter(Role.role_id == user.role_id).first()
    return UserListItem(
        user_id=user.user_id, name=user.name, email=user.email,
        role=role.name, is_active=user.is_active
    )


@router.put("/me/name")
def update_my_name(
    data: UpdateNameRequest,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user_payload)
):
    user = db.query(User).filter(User.user_id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    user.name = data.name
    db.commit()
    return {"user_id": user.user_id, "name": user.name}