from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from app.models.security import Role
from app.api.v1.auth import router as auth_router

app = FastAPI(title="Torre de Cartas API")

app.include_router(auth_router)


@app.get("/")
def read_root():
    return {"status": "ok", "message": "Torre de Cartas API funcionando"}

@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT 1"))
    return {"database": "conectado", "resultado": result.scalar()}

@app.get("/test-models")
def test_models(db: Session = Depends(get_db)):
    roles = db.query(Role).all()
    return [{"id": r.role_id, "name": r.name} for r in roles]