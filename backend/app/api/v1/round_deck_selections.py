from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user_payload
from app.schemas.round_deck_selection import DeckSelectionCreate, DeckSelectionResponse
from app.models.tournaments import RoundDeckSelection
from app.models.players import Player, Deck, DeckCard

router = APIRouter(prefix="/rounds", tags=["round-deck-selection"])

MIN_CARDS_PER_DECK = 20

@router.post("/{round_id}/deck-selection", response_model=DeckSelectionResponse)
def select_deck_for_round(
    round_id: int,
    data: DeckSelectionCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user_payload)
):
    player = db.query(Player).filter(Player.user_id == int(payload["sub"])).first()
    if not player:
        raise HTTPException(status_code=404, detail="No tienes perfil de jugador")

    deck = db.query(Deck).filter(
        Deck.deck_id == data.deck_id,
        Deck.player_id == player.player_id
    ).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Mazo no encontrado o no te pertenece")

    from sqlalchemy import func
    card_count = db.query(func.sum(DeckCard.quantity)).filter(DeckCard.deck_id == deck.deck_id).scalar() or 0
    if card_count < MIN_CARDS_PER_DECK:
        raise HTTPException(
            status_code=400,
            detail=f"El mazo debe tener al menos {MIN_CARDS_PER_DECK} cartas (tiene {card_count})"
        )

    existing = db.query(RoundDeckSelection).filter(
        RoundDeckSelection.round_id == round_id,
        RoundDeckSelection.player_id == player.player_id
    ).first()

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