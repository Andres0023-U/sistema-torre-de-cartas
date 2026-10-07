from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.security import User, Role

db = SessionLocal()

player_role = db.query(Role).filter(Role.name == "player").first()

new_user = User(
    name="Jugador Prueba Nuevo",
    email="jugadorprueba2@test.com",
    password_hash=hash_password("Clave1234"),
    role_id=player_role.role_id
)

db.add(new_user)
db.commit()
db.refresh(new_user)

print(f"Usuario creado: id={new_user.user_id}, email={new_user.email}")

db.close()

"""
{
  "email": "jugadorprueba2@test.com",
  "password": "Clave1234"
}
"""