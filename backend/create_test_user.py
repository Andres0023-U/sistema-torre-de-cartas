from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.security import User

db = SessionLocal()

test_user = User(
    name="Usuario Prueba",
    email="prueba@test.com",
    password_hash=hash_password("123456"),
    role_id=6,  # el ID de 'player' que viste en /test-models — ajústalo si quieres otro rol
)

db.add(test_user)
db.commit()
db.refresh(test_user)

print(f"Usuario creado: id={test_user.user_id}, email={test_user.email}")

db.close()