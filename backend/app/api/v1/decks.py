from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user_payload, require_role
from app.schemas.deck import DeckCreate, DeckUpdate, DeckResponse, DEFAULT_DECK_NAME
from app.schemas.deck_card import DeckCardCreate, DeckCardResponse
from app.models.players import Deck, Player, DeckCard
from app.models.cards import Card
from app.models.tournaments import RoundDeckSelection
from app.models.matches import Match, Result

router = APIRouter(prefix="/decks", tags=["decks"])

DEFAULT_DECK_COMPOSITION = [
    ("Ataque Básico", 4),
    ("Ataque Normal", 3),
    ("Ataque Fuerte", 2),
    ("Ataque Devastador", 1),
    ("Defensa Básica", 4),
    ("Defensa Normal", 3),
    ("Defensa Fuerte", 2),
    ("Defensa Implacable", 1),
]


def populate_default_deck_cards(deck_id: int, db: Session) -> None:
    """Agrega la composición balanceada de 20 cartas a un mazo por defecto."""
    card_names = [name for name, _ in DEFAULT_DECK_COMPOSITION]
    cards = db.query(Card).filter(Card.card_name.in_(card_names)).all()
    card_map = {card.card_name: card.card_id for card in cards}

    for card_name, quantity in DEFAULT_DECK_COMPOSITION:
        card_id = card_map.get(card_name)
        if card_id is None:
            continue
        existing = db.query(DeckCard).filter(
            DeckCard.deck_id == deck_id,
            DeckCard.card_id == card_id,
        ).first()
        if not existing:
            db.add(DeckCard(deck_id=deck_id, card_id=card_id, quantity=quantity))


def ensure_player_has_default_deck(player_id: int, db: Session) -> Deck:
    """Garantiza que el jugador tenga al menos un 'Mazo por defecto' con 20 cartas."""
    existing_decks = (
        db.query(Deck)
        .filter(Deck.player_id == player_id)
        .order_by(Deck.deck_id.asc())
        .all()
    )
    if existing_decks:
        first_deck = existing_decks[0]
        if len(existing_decks) == 1 and first_deck.name == DEFAULT_DECK_NAME:
            has_cards = (
                db.query(DeckCard)
                .filter(DeckCard.deck_id == first_deck.deck_id)
                .count()
            )
            if has_cards == 0:
                populate_default_deck_cards(first_deck.deck_id, db)
        return first_deck

    default_deck = Deck(player_id=player_id, name=DEFAULT_DECK_NAME)
    db.add(default_deck)
    db.flush()
    populate_default_deck_cards(default_deck.deck_id, db)
    return default_deck


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
    payload: dict = Depends(require_role(["player"]))
):
    name = data.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="El nombre del mazo no puede estar vacío")
    if len(name) > 50:
        raise HTTPException(status_code=400, detail="El nombre del mazo no puede superar los 50 caracteres")

    player = get_player_or_404(int(payload["sub"]), db)
    deck = Deck(player_id=player.player_id, name=name)
    db.add(deck)
    db.commit()
    db.refresh(deck)
    return deck


@router.get("/me", response_model=list[DeckResponse])
def list_my_decks(
    db: Session = Depends(get_db),
    payload: dict = Depends(require_role(["player"]))
):
    player = get_player_or_404(int(payload["sub"]), db)
    decks = (
        db.query(Deck)
        .filter(Deck.player_id == player.player_id)
        .order_by(Deck.deck_id.asc())
        .all()
    )
    if not decks:
        default_deck = ensure_player_has_default_deck(player.player_id, db)
        db.commit()
        db.refresh(default_deck)
        return [default_deck]
    return decks


@router.put("/{deck_id}", response_model=DeckResponse)
def update_deck(
    deck_id: int,
    data: DeckUpdate,
    db: Session = Depends(get_db),
    payload: dict = Depends(require_role(["player"]))
):
    name = data.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="El nombre del mazo no puede estar vacío")
    if len(name) > 50:
        raise HTTPException(status_code=400, detail="El nombre del mazo no puede superar los 50 caracteres")

    player = get_player_or_404(int(payload["sub"]), db)
    deck = get_my_deck_or_404(deck_id, player, db)
    deck.name = name
    db.commit()
    db.refresh(deck)
    return deck


@router.delete("/{deck_id}", status_code=204)
def delete_deck(
    deck_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(require_role(["player"]))
):
    player = get_player_or_404(int(payload["sub"]), db)
    deck = get_my_deck_or_404(deck_id, player, db)

    total_decks = db.query(Deck).filter(Deck.player_id == player.player_id).count()
    if total_decks <= 1:
        raise HTTPException(status_code=400, detail="Debes conservar al menos un mazo")

    in_round = db.query(RoundDeckSelection).filter(RoundDeckSelection.deck_id == deck_id).first()
    in_match = db.query(Match).filter((Match.deck1_id == deck_id) | (Match.deck2_id == deck_id)).first()
    in_result = db.query(Result).filter(Result.winner_id == deck_id).first()
    if in_round or in_match or in_result:
        raise HTTPException(
            status_code=400,
            detail="No puedes eliminar este mazo porque ya está en uso en un torneo o partida"
        )

    db.query(DeckCard).filter(DeckCard.deck_id == deck_id).delete(synchronize_session=False)
    db.delete(deck)
    db.commit()


@router.post("/{deck_id}/cards", response_model=DeckCardResponse)
def add_card_to_deck(
    deck_id: int,
    data: DeckCardCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(require_role(["player"]))
):
    player = get_player_or_404(int(payload["sub"]), db)
    get_my_deck_or_404(deck_id, player, db)

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
    payload: dict = Depends(require_role(["player"]))
):
    player = get_player_or_404(int(payload["sub"]), db)
    get_my_deck_or_404(deck_id, player, db)
    return db.query(DeckCard).filter(DeckCard.deck_id == deck_id).all()


@router.put("/{deck_id}/cards/{card_id}", response_model=DeckCardResponse)
def update_card_quantity(
    deck_id: int,
    card_id: int,
    data: DeckCardCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(require_role(["player"]))
):
    player = get_player_or_404(int(payload["sub"]), db)
    get_my_deck_or_404(deck_id, player, db)

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
    payload: dict = Depends(require_role(["player"]))
):
    player = get_player_or_404(int(payload["sub"]), db)
    get_my_deck_or_404(deck_id, player, db)

    deck_card = db.query(DeckCard).filter(
        DeckCard.deck_id == deck_id,
        DeckCard.card_id == card_id
    ).first()
    if not deck_card:
        raise HTTPException(status_code=404, detail="Esa carta no está en el mazo")

    db.delete(deck_card)
    db.commit()


# Abierto a cualquier usuario autenticado: round-detail lo usa para mostrar
# de quién es cada mazo, y esa pantalla la abre el organizador.
@router.get("/{deck_id}", response_model=DeckResponse)
def get_deck(
    deck_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user_payload)
):
    deck = db.query(Deck).filter(Deck.deck_id == deck_id).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Mazo no encontrado")
    return deck