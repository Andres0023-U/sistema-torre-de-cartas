from pydantic import BaseModel, field_validator
from typing import Literal

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