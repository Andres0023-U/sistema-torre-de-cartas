from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_role
from app.schemas.round_deck_selection import DeckSelectionCreate, DeckSelectionResponse
from app.models.tournaments import Round, RoundDeckSelection, TournamentRegistration
from app.models.matches import Match
from app.models.players import Player, Deck, DeckCard

router = APIRouter(prefix="/rounds", tags=["round-deck-selection"])

MIN_CARDS_PER_DECK = 20


@router.post("/{round_id}/deck-selection", response_model=DeckSelectionResponse)
def select_deck_for_round(
    round_id: int,
    data: DeckSelectionCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(require_role(["player"]))
):
    player = db.query(Player).filter(Player.user_id == int(payload["sub"])).first()
    if not player:
        raise HTTPException(status_code=404, detail="No tienes perfil de jugador")

    round_obj = db.query(Round).filter(Round.round_id == round_id).first()
    if not round_obj:
        raise HTTPException(status_code=404, detail="Ronda no encontrada")

    # Solo se puede cambiar de mazo antes de que la ronda empiece
    has_matches = db.query(Match).filter(Match.round_id == round_id).first()
    if round_obj.status != "pending" or has_matches:
        raise HTTPException(status_code=400, detail="La ronda ya empezó, no se puede cambiar de mazo")

    registered = db.query(TournamentRegistration).filter(
        TournamentRegistration.tournament_id == round_obj.tournament_id,
        TournamentRegistration.player_id == player.player_id
    ).first()
    if not registered:
        raise HTTPException(status_code=403, detail="No estás inscrito en este torneo")

    existing = db.query(RoundDeckSelection).filter(
        RoundDeckSelection.round_id == round_id,
        RoundDeckSelection.player_id == player.player_id
    ).first()

    # Después de la ronda 1, solo siguen los ganadores (ya tienen selección)
    if round_obj.number > 1 and not existing:
        raise HTTPException(status_code=403, detail="Fuiste eliminado de este torneo")

    deck = db.query(Deck).filter(
        Deck.deck_id == data.deck_id,
        Deck.player_id == player.player_id
    ).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Mazo no encontrado o no te pertenece")

    card_count = db.query(func.sum(DeckCard.quantity)).filter(DeckCard.deck_id == deck.deck_id).scalar() or 0
    if card_count < MIN_CARDS_PER_DECK:
        raise HTTPException(
            status_code=400,
            detail=f"El mazo debe tener al menos {MIN_CARDS_PER_DECK} cartas (tiene {card_count})"
        )

    if existing:
        existing.deck_id = deck.deck_id
        db.commit()
        db.refresh(existing)
        return existing

    selection = RoundDeckSelection(
        round_id=round_id,
        player_id=player.player_id,
        deck_id=deck.deck_id
    )
    db.add(selection)
    db.commit()
    db.refresh(selection)
    return selection


@router.get("/{round_id}/deck-selection", response_model=DeckSelectionResponse)
def get_my_deck_selection(
    round_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(require_role(["player"]))
):
    player = db.query(Player).filter(Player.user_id == int(payload["sub"])).first()
    if not player:
        raise HTTPException(status_code=404, detail="No tienes perfil de jugador")

    selection = db.query(RoundDeckSelection).filter(
        RoundDeckSelection.round_id == round_id,
        RoundDeckSelection.player_id == player.player_id
    ).first()

    if not selection:
        raise HTTPException(status_code=404, detail="Todavía no has elegido mazo para esta ronda")

    return selection