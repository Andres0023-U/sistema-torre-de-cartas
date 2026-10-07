from functools import cmp_to_key
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user_payload, require_role
from app.models.matches import Match, Result
from app.models.players import Deck, Player
from app.models.security import User

router = APIRouter(prefix="/ranking", tags=["ranking"])


@router.get("/")
def global_ranking(
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user_payload)
):
    rows = (
        db.query(Result, Match)
        .join(Match, Result.match_id == Match.match_id)
        .all()
    )

    stats: dict[int, dict] = {}
    # head_to_head[(min_id, max_id)] = {player_id: wins}
    head_to_head: dict[tuple[int, int], dict[int, int]] = {}

    def ensure(player_id: int):
        if player_id not in stats:
            stats[player_id] = {"played": 0, "won": 0, "points": 0, "last_date": None}
        return stats[player_id]

    deck_to_player: dict[int, int] = {}

    def get_player_id(deck_id: int) -> int:
        if deck_id not in deck_to_player:
            deck = db.query(Deck).filter(Deck.deck_id == deck_id).first()
            deck_to_player[deck_id] = deck.player_id
        return deck_to_player[deck_id]

    for result, match in rows:
        p1 = get_player_id(match.deck1_id)
        p2 = get_player_id(match.deck2_id)
        winner_player = get_player_id(result.winner_id)

        for pid, points in ((p1, result.player1_points), (p2, result.player2_points)):
            s = ensure(pid)
            s["played"] += 1
            s["points"] += points
            if pid == winner_player:
                s["won"] += 1
            if s["last_date"] is None or result.date > s["last_date"]:
                s["last_date"] = result.date

        key = (min(p1, p2), max(p1, p2))
        if key not in head_to_head:
            head_to_head[key] = {p1: 0, p2: 0}
        head_to_head[key][winner_player] += 1

    entries = []
    for player_id, s in stats.items():
        player = db.query(Player).filter(Player.player_id == player_id).first()
        user = db.query(User).filter(User.user_id == player.user_id).first()
        entries.append({
            "player_id": player_id,
            "name": user.name,
            "played": s["played"],
            "won": s["won"],
            "lost": s["played"] - s["won"],
            "points": s["points"],
            "last_result_date": s["last_date"].isoformat() if s["last_date"] else None,
            "_last_date_raw": s["last_date"],
        })

    def compare(a: dict, b: dict) -> int:
        if a["won"] != b["won"]:
            return -1 if a["won"] > b["won"] else 1
        if a["points"] != b["points"]:
            return -1 if a["points"] > b["points"] else 1

        key = (min(a["player_id"], b["player_id"]), max(a["player_id"], b["player_id"]))
        h2h = head_to_head.get(key)
        if h2h:
            wins_a = h2h.get(a["player_id"], 0)
            wins_b = h2h.get(b["player_id"], 0)
            if wins_a != wins_b:
                return -1 if wins_a > wins_b else 1

        date_a = a["_last_date_raw"]
        date_b = b["_last_date_raw"]
        if date_a != date_b:
            if date_a is None:
                return 1
            if date_b is None:
                return -1
            return -1 if date_a < date_b else 1

        return 0

    entries.sort(key=cmp_to_key(compare))

    ranking = []
    position = 0
    prev_entry = None
    for e in entries:
        if prev_entry is None or compare(prev_entry, e) != 0:
            position += 1
        e.pop("_last_date_raw")
        ranking.append({"position": position, **e})
        prev_entry = e

    return {"ranking": ranking}

@router.get("/me")
def my_stats(
    db: Session = Depends(get_db),
    payload: dict = Depends(require_role(["player"]))
):
    from app.models.tournaments import Round, Tournament

    player = db.query(Player).filter(Player.user_id == int(payload["sub"])).first()
    if not player:
        raise HTTPException(status_code=404, detail="No tienes perfil de jugador")

    full_ranking = global_ranking(db=db, payload=payload)["ranking"]
    my_entry = next((e for e in full_ranking if e["player_id"] == player.player_id), None)

    if not my_entry:
        my_entry = {
            "player_id": player.player_id, "name": None, "position": None,
            "played": 0, "won": 0, "lost": 0, "points": 0, "last_result_date": None
        }

    finished_tournaments = db.query(Tournament).filter(Tournament.status == "finished").all()
    tournaments_won = 0

    for t in finished_tournaments:
        last_round = (
            db.query(Round)
            .filter(Round.tournament_id == t.tournament_id)
            .order_by(Round.number.desc())
            .first()
        )
        if not last_round:
            continue

        final_match = db.query(Match).filter(Match.round_id == last_round.round_id).first()
        if not final_match:
            continue

        result = db.query(Result).filter(Result.match_id == final_match.match_id).first()
        if not result:
            continue

        winner_deck = db.query(Deck).filter(Deck.deck_id == result.winner_id).first()
        if winner_deck and winner_deck.player_id == player.player_id:
            tournaments_won += 1

    return {**my_entry, "tournaments_won": tournaments_won}