from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user_payload
from app.schemas.deck import DeckCreate, DeckResponse
from app.schemas.deck_card import DeckCardCreate, DeckCardResponse
from app.models.players import Deck, Player, DeckCard
from app.models.cards import Card

router = APIRouter(prefix="/decks", tags=["decks"])


def get_player_or_404(user_id: int, db: Session) -> Player:
    player = db.query(Player).filter(Player.user_id == user_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Primero debes crear tu perfil de jugador")
    return player


def get_my_deck_or_404(deck_id: int, player: Player, db: Session) -> Deck:
    deck = db.query(Deck).filter(
        Deck.deck_id == deck_id,
        Deck.player_id == player.player_id
    ).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Mazo no encontrado o no te pertenece")
    return deck


@router.post("/", response_model=DeckResponse)
def create_deck(
    data: DeckCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user_payload)
):
    player = get_player_or_404(int(payload["sub"]), db)
    deck = Deck(player_id=player.player_id, name=data.name)
    db.add(deck)
    db.commit()
    db.refresh(deck)
    return deck


@router.get("/me", response_model=list[DeckResponse])
def list_my_decks(
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user_payload)
):
    player = get_player_or_404(int(payload["sub"]), db)
    return db.query(Deck).filter(Deck.player_id == player.player_id).all()


@router.post("/{deck_id}/cards", response_model=DeckCardResponse)
def add_card_to_deck(
    deck_id: int,
    data: DeckCardCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user_payload)
):
    player = get_player_or_404(int(payload["sub"]), db)
    deck = get_my_deck_or_404(deck_id, player, db)

    card = db.query(Card).filter(Card.card_id == data.card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Carta no encontrada")

    if data.quantity > card.max_quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Máximo {card.max_quantity} copias de '{card.card_name}' por mazo"
        )

    existing = db.query(DeckCard).filter(
        DeckCard.deck_id == deck_id,
        DeckCard.card_id == data.card_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Esa carta ya está en el mazo, usa el endpoint de actualizar")

    deck_card = DeckCard(deck_id=deck_id, card_id=data.card_id, quantity=data.quantity)
    db.add(deck_card)
    db.commit()
    db.refresh(deck_card)
    return deck_card


@router.get("/{deck_id}/cards", response_model=list[DeckCardResponse])
def list_deck_cards(
    deck_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user_payload)
):
    player = get_player_or_404(int(payload["sub"]), db)
    get_my_deck_or_404(deck_id, player, db)
    return db.query(DeckCard).filter(DeckCard.deck_id == deck_id).all()

from app.schemas.deck_card import DeckCardCreate, DeckCardResponse

@router.put("/{deck_id}/cards/{card_id}", response_model=DeckCardResponse)
def update_card_quantity(
    deck_id: int,
    card_id: int,
    data: DeckCardCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user_payload)
):
    player = get_player_or_404(int(payload["sub"]), db)
    deck = get_my_deck_or_404(deck_id, player, db)

    card = db.query(Card).filter(Card.card_id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Carta no encontrada")

    if data.quantity > card.max_quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Máximo {card.max_quantity} copias de '{card.card_name}' por mazo"
        )

    deck_card = db.query(DeckCard).filter(
        DeckCard.deck_id == deck_id,
        DeckCard.card_id == card_id
    ).first()
    if not deck_card:
        raise HTTPException(status_code=404, detail="Esa carta no está en el mazo")

    deck_card.quantity = data.quantity
    db.commit()
    db.refresh(deck_card)
    return deck_card


@router.delete("/{deck_id}/cards/{card_id}", status_code=204)
def remove_card_from_deck(
    deck_id: int,
    card_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user_payload)
):
    player = get_player_or_404(int(payload["sub"]), db)
    deck = get_my_deck_or_404(deck_id, player, db)

    deck_card = db.query(DeckCard).filter(
        DeckCard.deck_id == deck_id,
        DeckCard.card_id == card_id
    ).first()
    if not deck_card:
        raise HTTPException(status_code=404, detail="Esa carta no está en el mazo")

    db.delete(deck_card)
    db.commit()