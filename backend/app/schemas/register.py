from pydantic import BaseModel, EmailStr, field_validator
import re

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El nombre no puede estar vacío")
        if len(v) > 20:
            raise ValueError("El nombre no puede tener más de 20 caracteres")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("La contraseña debe tener al menos una letra")
        if not re.search(r"[0-9]", v):
            raise ValueError("La contraseña debe tener al menos un número")
        return v