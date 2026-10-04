from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from app.models.security import Role
from app.api.v1.auth import router as auth_router
from app.api.v1.tournaments import router as tournaments_router
from app.api.v1.players import router as players_router
from app.api.v1.decks import router as decks_router
from app.api.v1.round_deck_selections import router as round_deck_router
from app.api.v1.matches import router as matches_router

app = FastAPI(title="Torre de Cartas API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(tournaments_router)
app.include_router(players_router)
app.include_router(decks_router)
app.include_router(round_deck_router)
app.include_router(matches_router)


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