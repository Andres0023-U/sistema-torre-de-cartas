from app.core.database import SessionLocal
from app.models.security import User
from app.models.players import Player, Deck, DeckCard

db = SessionLocal()

user = db.query(User).filter(User.email == "jugadorprueba2@test.com").first()
player = db.query(Player).filter(Player.user_id == user.user_id).first()

deck = Deck(player_id=player.player_id, name="Mazo de prueba")
db.add(deck)
db.commit()
db.refresh(deck)

cartas = [
    (1, 4), (2, 3), (3, 2), (4, 1),
    (5, 4), (6, 3), (7, 2), (8, 1),
]

for card_id, quantity in cartas:
    db.add(DeckCard(deck_id=deck.deck_id, card_id=card_id, quantity=quantity))

db.commit()

print(f"Mazo creado: deck_id={deck.deck_id}, 20 cartas agregadas, player_id={player.player_id}")

db.close()