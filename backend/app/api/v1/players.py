from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user_payload
from app.schemas.player import PlayerResponse
from app.models.players import Player

router = APIRouter(prefix="/players", tags=["players"])

@router.post("/me", response_model=PlayerResponse)
def create_my_player(
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user_payload)
):
    user_id = int(payload["sub"])

    existing = db.query(Player).filter(Player.user_id == user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ya tienes un perfil de jugador")

    player = Player(user_id=user_id)
    db.add(player)
    db.commit()
    db.refresh(player)
    return player

@router.get("/me", response_model=PlayerResponse)
def get_my_player(
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user_payload)
):
    user_id = int(payload["sub"])
    player = db.query(Player).filter(Player.user_id == user_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="No tienes perfil de jugador todavía")
    return player