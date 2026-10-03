from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.security import User

db = SessionLocal()

organizer = User(
    name="Organizador Prueba",
    email="organizador@test.com",
    password_hash=hash_password("123456"),
    role_id=5,  # el ID de 'organizer' que viste antes
)

db.add(organizer)
db.commit()
db.refresh(organizer)

print(f"Usuario creado: id={organizer.user_id}, email={organizer.email}")

db.close()