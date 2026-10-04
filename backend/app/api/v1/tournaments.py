from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_role, get_current_user_payload
from app.schemas.tournament import TournamentCreate, TournamentResponse
from app.models.tournaments import Tournament

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

@router.post("/{tournament_id}/registrations", response_model=RegistrationResponse)
def register_player(
    tournament_id: int,
    data: RegistrationCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(require_role(["organizer"]))
):
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