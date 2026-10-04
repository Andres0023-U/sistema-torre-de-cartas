from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_role, get_current_user_payload
from app.schemas.tournament import TournamentCreate, TournamentResponse
from app.models.tournaments import Tournament
from app.models.matches import Match, Result
from app.models.tournaments import Round, RoundDeckSelection
from app.models.players import Deck

router = APIRouter(prefix="/tournaments", tags=["tournaments"])

@router.post("/", response_model=TournamentResponse)
def create_tournament(
    data: TournamentCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(require_role(["organizer"]))
):
    new_tournament = Tournament(
        name=data.name,
        date=data.date,
        format=data.format,
        num_players=data.num_players,
        status="pending",
        organizer_id=int(payload["sub"])
    )
    db.add(new_tournament)
    db.commit()
    db.refresh(new_tournament)
    return new_tournament

@router.get("/", response_model=list[TournamentResponse])
def list_tournaments(
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user_payload)
):
    return db.query(Tournament).all()

from app.models.tournaments import TournamentRegistration
from app.schemas.tournament_registration import RegistrationCreate, RegistrationResponse

def count_registrations(db: Session, tournament_id: int) -> int:
    return db.query(func.count(TournamentRegistration.tournament_registration_id)).filter(
        TournamentRegistration.tournament_id == tournament_id
    ).scalar()


@router.post("/{tournament_id}/registrations", response_model=RegistrationResponse)
def register_player(
    tournament_id: int,
    data: RegistrationCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(require_role(["organizer"]))
):
    tournament = db.query(Tournament).filter(Tournament.tournament_id == tournament_id).first()
    if not tournament:
        raise HTTPException(status_code=404, detail="Torneo no encontrado")

    if tournament.organizer_id != int(payload["sub"]):
        raise HTTPException(status_code=403, detail="Solo el organizador del torneo puede inscribir jugadores")

    if tournament.status != "pending":
        raise HTTPException(status_code=400, detail="Solo se puede inscribir en torneos que no han iniciado")

    already = db.query(TournamentRegistration).filter(
        TournamentRegistration.tournament_id == tournament_id,
        TournamentRegistration.player_id == data.player_id
    ).first()
    if already:
        raise HTTPException(status_code=400, detail="El jugador ya está inscrito en este torneo")

    inscritos = count_registrations(db, tournament_id)
    if inscritos >= tournament.num_players:
        raise HTTPException(
            status_code=400,
            detail=f"El torneo ya está completo ({inscritos}/{tournament.num_players})"
        )

    registration = TournamentRegistration(
        tournament_id=tournament_id,
        player_id=data.player_id
    )
    db.add(registration)
    db.commit()
    db.refresh(registration)
    return registration
@router.get("/{tournament_id}/registrations", response_model=list[RegistrationResponse])
def list_registrations(
    tournament_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user_payload)
):
    return db.query(TournamentRegistration).filter(
        TournamentRegistration.tournament_id == tournament_id
    ).all()

@router.post("/{tournament_id}/start")
def start_tournament(
    tournament_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(require_role(["organizer"]))
):
    tournament = db.query(Tournament).filter(Tournament.tournament_id == tournament_id).first()
    if not tournament:
        raise HTTPException(status_code=404, detail="Torneo no encontrado")

    if tournament.organizer_id != int(payload["sub"]):
        raise HTTPException(status_code=403, detail="Solo el organizador del torneo puede iniciarlo")

    if tournament.status != "pending":
        raise HTTPException(status_code=400, detail="El torneo ya fue iniciado o finalizado")

    inscritos = count_registrations(db, tournament_id)
    if inscritos != tournament.num_players:
        raise HTTPException(
            status_code=400,
            detail=f"El torneo requiere {tournament.num_players} jugadores inscritos y tiene {inscritos}"
        )

    tournament.status = "in_progress"

    first_round = Round(
        tournament_id=tournament_id,
        number=1,
        name="Ronda 1",
        status="pending",
    )
    db.add(first_round)
    db.commit()
    db.refresh(tournament)
    db.refresh(first_round)

    return {
        "tournament_id": tournament.tournament_id,
        "status": tournament.status,
        "round_id": first_round.round_id,
    }

@router.post("/{tournament_id}/next-round")
def next_round(
    tournament_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(require_role(["organizer"]))
):
    tournament = db.query(Tournament).filter(Tournament.tournament_id == tournament_id).first()
    if not tournament:
        raise HTTPException(status_code=404, detail="Torneo no encontrado")
    if tournament.organizer_id != int(payload["sub"]):
        raise HTTPException(status_code=403, detail="Solo el organizador del torneo puede avanzar de ronda")
    if tournament.status != "in_progress":
        raise HTTPException(status_code=400, detail="El torneo no está en curso")

    last_round = db.query(Round).filter(Round.tournament_id == tournament_id) \
        .order_by(Round.number.desc()).first()
    if not last_round:
        raise HTTPException(status_code=400, detail="El torneo no tiene rondas")

    matches = db.query(Match).filter(Match.round_id == last_round.round_id) \
        .order_by(Match.match_id.asc()).all()
    if not matches:
        raise HTTPException(status_code=400, detail="La ronda actual no tiene emparejamientos")

    winners: list[int] = []
    pending: list[int] = []
    for m in matches:
        result = db.query(Result).filter(Result.match_id == m.match_id).first()
        if not result:
            pending.append(m.match_id)
        else:
            winners.append(result.winner_id)   # winner_id es un deck_id
    if pending:
        raise HTTPException(status_code=400, detail=f"Faltan resultados de los matches: {pending}")

    last_round.status = "finished"

    # Un solo ganador: el torneo terminó
    if len(winners) == 1:
        tournament.status = "finished"
        db.commit()
        deck = db.query(Deck).filter(Deck.deck_id == winners[0]).first()
        return {"status": "finished", "champion_deck_id": winners[0],
                "champion_player_id": deck.player_id}

    new_round = Round(
        tournament_id=tournament_id,
        number=last_round.number + 1,
        name=f"Ronda {last_round.number + 1}",
        status="pending",   # sin matches: los jugadores pueden cambiar de mazo
    )
    db.add(new_round)
    db.flush()

    # Cada ganador queda preseleccionado con el mazo con el que ganó.
    selections = []
    for deck_id in winners:
        deck = db.query(Deck).filter(Deck.deck_id == deck_id).first()
        sel = RoundDeckSelection(round_id=new_round.round_id,
                                 player_id=deck.player_id, deck_id=deck_id)
        db.add(sel)
        selections.append(sel)

    db.commit()

    return {
        "status": "in_progress",
        "round_id": new_round.round_id,
        "round_number": new_round.number,
        "round_status": "pending",
        "players": [{"player_id": s.player_id, "deck_id": s.deck_id} for s in selections],
    }