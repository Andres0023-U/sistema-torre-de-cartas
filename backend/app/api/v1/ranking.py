from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user_payload
from app.core.access import require_tournament_access
from app.models.matches import Match, Result
from app.models.players import Deck, Player
from app.models.security import User
from app.models.tournaments import Round, TournamentRegistration

router = APIRouter(tags=["ranking"])

# Grupo de quien nunca ha perdido (campeón o, si el torneo sigue, jugador vivo)
ALIVE = 10**6


class RankingEntry(BaseModel):
    position: int
    player_id: int
    name: str
    played: int
    won: int
    lost: int
    points: int
    life: int
    eliminated_round: int | None


class TournamentRankingResponse(BaseModel):
    tournament_id: int
    final: bool
    ranking: list[RankingEntry]


@router.get("/tournaments/{tournament_id}/ranking", response_model=TournamentRankingResponse)
def tournament_ranking(
    tournament_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user_payload)
):
    tournament = require_tournament_access(db, payload, tournament_id)

    rows = (
        db.query(Player, User)
        .join(TournamentRegistration, TournamentRegistration.player_id == Player.player_id)
        .join(User, User.user_id == Player.user_id)
        .filter(TournamentRegistration.tournament_id == tournament_id)
        .all()
    )

    stats = {
        p.player_id: {
            "name": u.name, "played": 0, "won": 0, "lost": 0,
            "points": 0, "life": 0, "lost_round": None
        }
        for p, u in rows
    }

    # Solo matches del torneo que ya tienen resultado
    matches = (
        db.query(Match, Result, Round)
        .join(Round, Round.round_id == Match.round_id)
        .join(Result, Result.match_id == Match.match_id)
        .filter(Round.tournament_id == tournament_id)
        .all()
    )

    deck_ids = {m.deck1_id for m, _, _ in matches} | {m.deck2_id for m, _, _ in matches}
    owners = {}
    if deck_ids:
        owners = {
            d.deck_id: d.player_id
            for d in db.query(Deck).filter(Deck.deck_id.in_(deck_ids)).all()
        }

    for match, result, rnd in matches:
        sides = (
            (match.deck1_id, result.player1_points, result.player1_final_life),
            (match.deck2_id, result.player2_points, result.player2_final_life),
        )
        for deck_id, points, life in sides:
            player_id = owners.get(deck_id)
            if player_id not in stats:
                continue
            s = stats[player_id]
            s["played"] += 1
            s["points"] += points
            s["life"] += life
            if result.winner_id == deck_id:
                s["won"] += 1
            else:
                s["lost"] += 1
                s["lost_round"] = rnd.number

    def group(s: dict) -> int:
        if s["played"] == 0:
            return 0                  # nunca jugó
        if s["lost_round"] is not None:
            return s["lost_round"]    # ronda en la que fue eliminado
        return ALIVE                  # campeón o aún en competencia

    # Más lejos llegó, más puntos, más vida; player_id solo estabiliza el orden
    ordered = sorted(
        stats.items(),
        key=lambda kv: (-group(kv[1]), -kv[1]["points"], -kv[1]["life"], kv[0])
    )

    ranking: list[RankingEntry] = []
    previous_key = None
    position = 0
    for index, (player_id, s) in enumerate(ordered, start=1):
        key = (group(s), s["points"], s["life"])
        if key != previous_key:
            position = index          # iguales en todo comparten posición
            previous_key = key
        ranking.append(RankingEntry(
            position=position,
            player_id=player_id,
            name=s["name"],
            played=s["played"],
            won=s["won"],
            lost=s["lost"],
            points=s["points"],
            life=s["life"],
            eliminated_round=s["lost_round"],
        ))

    return TournamentRankingResponse(
        tournament_id=tournament_id,
        final=tournament.status == "finished",
        ranking=ranking,
    )