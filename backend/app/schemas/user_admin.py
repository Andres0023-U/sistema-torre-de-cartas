from pydantic import BaseModel
from typing import Literal

class AssignRoleRequest(BaseModel):
    role: Literal["organizer", "player"]

class UserAdminResponse(BaseModel):
    user_id: int
    name: str
    email: str
    role: str