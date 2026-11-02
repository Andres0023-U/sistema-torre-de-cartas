from pydantic import BaseModel, field_validator
from typing import Literal
import re

class AssignRoleRequest(BaseModel):
    role: Literal["organizer", "player"]

class UserAdminResponse(BaseModel):
    user_id: int
    name: str
    email: str
    role: str

class UserListItem(BaseModel):
    user_id: int
    name: str
    email: str
    role: str
    is_active: bool

class SetActiveRequest(BaseModel):
    is_active: bool

class UpdateNameRequest(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El nombre no puede estar vacío")
        if len(v) > 20:
            raise ValueError("El nombre no puede superar 20 caracteres")
        return v

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La nueva contraseña debe tener al menos 8 caracteres")
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("La nueva contraseña debe tener al menos una letra")
        if not re.search(r"[0-9]", v):
            raise ValueError("La nueva contraseña debe tener al menos un número")
        return v
