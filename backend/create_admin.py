from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.security import User, Role

db = SessionLocal()

admin_role = db.query(Role).filter(Role.name == "admin").first()

admin = User(
    name="Admin",
    email="admin@test.com",
    password_hash=hash_password("admin1234"),
    role_id=admin_role.role_id
)

db.add(admin)
db.commit()
db.refresh(admin)

print(f"Admin creado: id={admin.user_id}, email={admin.email}")

db.close()

"""
Nube
{
  "email": "admin@test.com",
  "password": "admin1234"
}
"""
"""
Local 
{
  "email": "admin@demo.com",
  "password": "Demo1234"
}
"""