from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.tournaments import Tournament, TournamentRegistration
from app.models.players import Player


def require_tournament_access(db: Session, payload: dict, tournament_id: int) -> Tournament:
    tournament = db.query(Tournament).filter(Tournament.tournament_id == tournament_id).first()
    if not tournament:
        raise HTTPException(status_code=404, detail="Torneo no encontrado")

    role = payload.get("role")

    # Organizador y admin ven todos los torneos
    if role in ("organizer", "admin"):
        return tournament

    # Jugador: solo si está inscrito
    if role == "player":
        player = db.query(Player).filter(Player.user_id == int(payload["sub"])).first()
        if player:
            registered = db.query(TournamentRegistration).filter(
                TournamentRegistration.tournament_id == tournament_id,
                TournamentRegistration.player_id == player.player_id
            ).first()
            if registered:
                return tournament

    raise HTTPException(status_code=403, detail="No participas en este torneo")