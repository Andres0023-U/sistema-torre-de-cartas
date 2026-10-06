from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_role
from app.schemas.player import PlayerResponse, PlayerWithUserResponse
from app.models.players import Player
from app.models.security import User, Role

router = APIRouter(prefix="/players", tags=["players"])


@router.post("/me", response_model=PlayerResponse)
def create_my_player(
    db: Session = Depends(get_db),
    payload: dict = Depends(require_role(["player"]))
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
    payload: dict = Depends(require_role(["player"]))
):
    user_id = int(payload["sub"])
    player = db.query(Player).filter(Player.user_id == user_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="No tienes perfil de jugador todavía")
    return player


@router.get("/", response_model=list[PlayerWithUserResponse])
def list_players(
    db: Session = Depends(get_db),
    payload: dict = Depends(require_role(["organizer"]))
):
    results = (
        db.query(Player, User)
        .join(User, Player.user_id == User.user_id)
        .join(Role, Role.role_id == User.role_id)
        .filter(Role.name == "player")
        .all()
    )
    return [
        PlayerWithUserResponse(
            player_id=player.player_id,
            user_id=player.user_id,
            name=user.name,
            email=user.email
        )
        for player, user in results
    ]