from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_role
from app.models.matches import Match, Result
from app.models.players import Deck, Player
from app.models.security import User
from app.models.tournaments import Round, Tournament

router = APIRouter(prefix="/players", tags=["history"])


class HistoryEntry(BaseModel):
    match_id: int
    tournament_id: int
    tournament_name: str
    round_number: int
    round_name: str
    opponent_player_id: int | None
    opponent_name: str | None
    won: bool
    points: int
    end_phase: str
    date: datetime


@router.get("/me/history", response_model=list[HistoryEntry])
def my_history(
    db: Session = Depends(get_db),
    payload: dict = Depends(require_role(["player"]))
):
    player = db.query(Player).filter(Player.user_id == int(payload["sub"])).first()
    if not player:
        raise HTTPException(status_code=404, detail="No tienes perfil de jugador")

    my_deck_ids = {
        d.deck_id for d in db.query(Deck).filter(Deck.player_id == player.player_id).all()
    }
    if not my_deck_ids:
        return []

    rows = (
        db.query(Match, Result, Round, Tournament)
        .join(Result, Result.match_id == Match.match_id)
        .join(Round, Round.round_id == Match.round_id)
        .join(Tournament, Tournament.tournament_id == Round.tournament_id)
        .filter(or_(Match.deck1_id.in_(my_deck_ids), Match.deck2_id.in_(my_deck_ids)))
        .order_by(Result.date.desc())
        .all()
    )

    # Dueño y nombre de los mazos rivales
    opponent_deck_ids = set()
    for match, _, _, _ in rows:
        opponent_deck_ids.add(match.deck2_id if match.deck1_id in my_deck_ids else match.deck1_id)

    opponents = {}
    if opponent_deck_ids:
        for deck, user, owner in (
            db.query(Deck, User, Player)
            .join(Player, Player.player_id == Deck.player_id)
            .join(User, User.user_id == Player.user_id)
            .filter(Deck.deck_id.in_(opponent_deck_ids))
            .all()
        ):
            opponents[deck.deck_id] = (owner.player_id, user.name)

    history = []
    for match, result, rnd, tournament in rows:
        is_p1 = match.deck1_id in my_deck_ids
        my_deck = match.deck1_id if is_p1 else match.deck2_id
        opponent_deck = match.deck2_id if is_p1 else match.deck1_id
        opponent_id, opponent_name = opponents.get(opponent_deck, (None, None))

        history.append(HistoryEntry(
            match_id=match.match_id,
            tournament_id=tournament.tournament_id,
            tournament_name=tournament.name,
            round_number=rnd.number,
            round_name=rnd.name,
            opponent_player_id=opponent_id,
            opponent_name=opponent_name,
            won=result.winner_id == my_deck,
            points=result.player1_points if is_p1 else result.player2_points,
            end_phase=result.end_phase,
            date=result.date,
        ))

    return history