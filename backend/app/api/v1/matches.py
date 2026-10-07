from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone
from app.core.database import get_db
from app.core.security import require_role, get_current_user_payload, MANAGER_ROLES, can_manage_tournament
from app.schemas.match import MatchCreate, MatchResponse, ResultCreate, ResultResponse
from app.models.matches import Match, Result
from app.models.tournaments import Round, TournamentRegistration, RoundDeckSelection
from app.models.players import Deck, DeckCard
from app.models.tournaments import Round, Tournament, TournamentRegistration, RoundDeckSelection
from app.core.access import require_tournament_access

router = APIRouter(prefix="/matches", tags=["matches"])

MIN_CARDS = 20
 

@router.post("/", response_model=MatchResponse)
def create_match(
    data: MatchCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(require_role(MANAGER_ROLES))
):
    if data.deck1_id == data.deck2_id:
        raise HTTPException(status_code=400, detail="Un mazo no puede enfrentarse a sí mismo")

    match = Match(round_id=data.round_id, deck1_id=data.deck1_id, deck2_id=data.deck2_id)
    db.add(match)
    db.commit()
    db.refresh(match)
    return match


@router.get("/", response_model=list[MatchResponse])
def list_matches(
    round_id: int | None = None,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user_payload)
):
    if round_id is not None:
        round_obj = db.query(Round).filter(Round.round_id == round_id).first()
        if not round_obj:
            raise HTTPException(status_code=404, detail="Ronda no encontrada")
        require_tournament_access(db, payload, round_obj.tournament_id)
        return db.query(Match).filter(Match.round_id == round_id).all()

    if payload.get("role") in ("organizer", "admin"):
        return db.query(Match).all()

    raise HTTPException(status_code=400, detail="Indica el round_id")


def calculate_points(end_phase: str, winner_life: int) -> int:
    if end_phase == "normal":
        return 3
    elif end_phase == "overtime":
        return 2 if winner_life > 0 else 1
    raise HTTPException(status_code=400, detail="end_phase debe ser 'normal' u 'overtime'")


@router.post("/{match_id}/result", response_model=ResultResponse)
def create_result(
    match_id: int,
    data: ResultCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(require_role(MANAGER_ROLES))
):
    match = db.query(Match).filter(Match.match_id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match no encontrado")

    round_obj = db.query(Round).filter(Round.round_id == match.round_id).first()
    tournament = db.query(Tournament).filter(
        Tournament.tournament_id == round_obj.tournament_id
    ).first()

    if not can_manage_tournament(payload, tournament):
        raise HTTPException(status_code=403, detail="Solo el organizador del torneo puede registrar resultados")

    if tournament.status != "in_progress":
        raise HTTPException(status_code=400, detail="Solo se pueden registrar resultados en torneos en curso")

    existing = db.query(Result).filter(Result.match_id == match_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Este match ya tiene un resultado registrado")

    if data.winner_id not in (match.deck1_id, match.deck2_id):
        raise HTTPException(status_code=400, detail="El ganador debe ser uno de los dos mazos del match")

    winner_is_p1 = data.winner_id == match.deck1_id
    winner_life = data.player1_final_life if winner_is_p1 else data.player2_final_life
    loser_life = data.player2_final_life if winner_is_p1 else data.player1_final_life

    if winner_life <= loser_life:
        raise HTTPException(
            status_code=400,
            detail="El ganador debe terminar con más vida que el perdedor"
        )

    winner_points = calculate_points(data.end_phase, winner_life)

    result = Result(
        match_id=match_id,
        winner_id=data.winner_id,
        end_phase=data.end_phase,
        player1_final_life=data.player1_final_life,
        player2_final_life=data.player2_final_life,
        player1_points=winner_points if winner_is_p1 else 0,
        player2_points=0 if winner_is_p1 else winner_points,
        date=data.date or datetime.now(timezone.utc),
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


@router.get("/{match_id}/result", response_model=ResultResponse)
def get_result(
    match_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user_payload)
):
    match = db.query(Match).filter(Match.match_id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match no encontrado")

    round_obj = db.query(Round).filter(Round.round_id == match.round_id).first()
    require_tournament_access(db, payload, round_obj.tournament_id)

    result = db.query(Result).filter(Result.match_id == match_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Este match no tiene resultado todavía")
    return result


@router.post("/generate/{round_id}", response_model=list[MatchResponse])
def generate_matches(
    round_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(require_role(MANAGER_ROLES))
):
    round_obj = db.query(Round).filter(Round.round_id == round_id).first()
    if not round_obj:
        raise HTTPException(status_code=404, detail="Ronda no encontrada")

    tournament = db.query(Tournament).filter(
        Tournament.tournament_id == round_obj.tournament_id
    ).first()

    if not can_manage_tournament(payload, tournament):
        raise HTTPException(status_code=403, detail="Solo el organizador del torneo puede generar emparejamientos")

    if tournament.status != "in_progress":
        raise HTTPException(status_code=400, detail="El torneo no ha iniciado, no se pueden generar emparejamientos")

    if db.query(Match).filter(Match.round_id == round_id).first():
        raise HTTPException(status_code=400, detail="Esta ronda ya tiene emparejamientos generados")

    deck_ids: list[int] = []

    if round_obj.number == 1:
        # Ronda 1: todos los inscritos
        registrations = db.query(TournamentRegistration).filter(
            TournamentRegistration.tournament_id == round_obj.tournament_id
        ).order_by(TournamentRegistration.tournament_registration_id.asc()).all()

        for reg in registrations:
            selection = db.query(RoundDeckSelection).filter(
                RoundDeckSelection.round_id == round_id,
                RoundDeckSelection.player_id == reg.player_id
            ).first()

            if selection:
                deck_ids.append(selection.deck_id)
                continue

            # no eligió mazo: usar el más antiguo que cumpla las 20 cartas
            candidates = db.query(Deck).filter(Deck.player_id == reg.player_id).order_by(Deck.deck_id.asc()).all()
            chosen = None
            for d in candidates:
                total = db.query(func.sum(DeckCard.quantity)).filter(DeckCard.deck_id == d.deck_id).scalar() or 0
                if total >= MIN_CARDS:
                    chosen = d
                    break

            if not chosen:
                continue  # sin mazo válido, queda fuera de esta ronda

            db.add(RoundDeckSelection(round_id=round_id, player_id=reg.player_id, deck_id=chosen.deck_id))
            deck_ids.append(chosen.deck_id)
    else:
        # Rondas siguientes: solo los ganadores, que next-round ya dejó con selección
        selections = db.query(RoundDeckSelection).filter(
            RoundDeckSelection.round_id == round_id
        ).order_by(RoundDeckSelection.round_deck_selection_id.asc()).all()
        deck_ids = [s.deck_id for s in selections]

    if len(deck_ids) < 2:
        db.rollback()
        raise HTTPException(status_code=400, detail="No hay suficientes jugadores con mazo válido")

    created = []
    for i in range(0, len(deck_ids) - 1, 2):
        m = Match(round_id=round_id, deck1_id=deck_ids[i], deck2_id=deck_ids[i + 1])
        db.add(m)
        created.append(m)

    round_obj.status = "in_progress"
    db.commit()
    for m in created:
        db.refresh(m)

    return created