"""
Seed de desarrollo: jugadores de prueba con perfil, mazo válido e inscripción opcional.
Uso (desde backend/):
    python -m scripts.seed_dev_data
    python -m scripts.seed_dev_data --tournament-id 3
Es idempotente: se puede correr varias veces sin duplicar datos.
"""
import argparse
from sqlalchemy import text

from app.core.database import SessionLocal
from app.core.security import hash_password

PASSWORD = "123456"

# (nombre, email, nombre del mazo, [(card_id, cantidad), ...])  -> cada mazo suma 20
PLAYERS = [
    ("Jugador Uno",    "jugador1@test.com", "Mazo Equilibrado",
     [(1, 4), (2, 3), (3, 2), (4, 1), (5, 4), (6, 3), (7, 2), (8, 1)]),
    ("Jugador Dos",    "jugador2@test.com", "Mazo Defensivo",
     [(5, 4), (6, 3), (7, 2), (8, 1), (9, 4), (10, 3), (11, 2), (12, 1)]),
    ("Jugador Tres",   "jugador3@test.com", "Mazo Mixto",
     [(1, 4), (2, 3), (3, 2), (4, 1), (9, 4), (10, 3), (11, 2), (12, 1)]),
    ("Jugador Cuatro", "jugador4@test.com", "Mazo Especiales",
     [(1, 4), (2, 3), (3, 2), (4, 1), (5, 4),
      (13, 1), (14, 1), (15, 1), (16, 1), (17, 1), (18, 1)]),
]


def get_or_create_user(db, name, email, role_id, password_hash):
    row = db.execute(text('SELECT user_id FROM security."user" WHERE email = :e'),
                     {"e": email}).first()
    if row:
        return row[0]
    return db.execute(text(
        'INSERT INTO security."user" (name, email, password_hash, role_id) '
        'VALUES (:n, :e, :p, :r) RETURNING user_id'),
        {"n": name, "e": email, "p": password_hash, "r": role_id}).scalar()


def get_or_create_player(db, user_id):
    row = db.execute(text('SELECT player_id FROM players.player WHERE user_id = :u'),
                     {"u": user_id}).first()
    if row:
        return row[0]
    return db.execute(text(
        'INSERT INTO players.player (user_id) VALUES (:u) RETURNING player_id'),
        {"u": user_id}).scalar()


def validate_deck(db, cards):
    total = sum(q for _, q in cards)
    if total < 20:
        raise ValueError(f"El mazo suma {total} cartas, mínimo 20")
    for card_id, qty in cards:
        max_q = db.execute(text('SELECT max_quantity FROM cards.card WHERE card_id = :c'),
                           {"c": card_id}).scalar()
        if max_q is None:
            raise ValueError(f"La carta {card_id} no existe")
        if qty > max_q:
            raise ValueError(f"Carta {card_id}: {qty} supera el máximo permitido ({max_q})")


def get_or_create_deck(db, player_id, deck_name, cards):
    row = db.execute(text(
        'SELECT deck_id FROM players.deck WHERE player_id = :p AND name = :n'),
        {"p": player_id, "n": deck_name}).first()
    if row:
        return row[0]
    validate_deck(db, cards)
    deck_id = db.execute(text(
        'INSERT INTO players.deck (player_id, name) VALUES (:p, :n) RETURNING deck_id'),
        {"p": player_id, "n": deck_name}).scalar()
    for card_id, qty in cards:
        db.execute(text(
            'INSERT INTO players.deck_card (deck_id, card_id, quantity) '
            'VALUES (:d, :c, :q)'), {"d": deck_id, "c": card_id, "q": qty})
    return deck_id


def register_in_tournament(db, tournament_id, player_id):
    num_players = db.execute(text(
        'SELECT num_players FROM tournaments.tournament WHERE tournament_id = :t'),
        {"t": tournament_id}).scalar()
    if num_players is None:
        raise ValueError(f"El torneo {tournament_id} no existe")
    inscritos = db.execute(text(
        'SELECT COUNT(*) FROM tournaments.tournament_registration WHERE tournament_id = :t'),
        {"t": tournament_id}).scalar()
    if inscritos >= num_players:
        print(f"  - torneo {tournament_id} ya está completo ({inscritos}/{num_players}), no se inscribe")
        return
    db.execute(text(
        'INSERT INTO tournaments.tournament_registration (tournament_id, player_id) '
        'VALUES (:t, :p) ON CONFLICT ON CONSTRAINT uq_tournament_registration_unique DO NOTHING'),
        {"t": tournament_id, "p": player_id})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tournament-id", type=int, default=None,
                        help="Si se indica, inscribe a los jugadores en ese torneo")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        role_id = db.execute(text("SELECT role_id FROM security.role WHERE name = 'player'")).scalar()
        if role_id is None:
            raise RuntimeError("No existe el rol 'player'. Corre primero seeds/00_roles.sql")

        password_hash = hash_password(PASSWORD)

        for name, email, deck_name, cards in PLAYERS:
            user_id = get_or_create_user(db, name, email, role_id, password_hash)
            player_id = get_or_create_player(db, user_id)
            deck_id = get_or_create_deck(db, player_id, deck_name, cards)
            if args.tournament_id:
                register_in_tournament(db, args.tournament_id, player_id)
            print(f"OK {email}: user={user_id} player={player_id} deck={deck_id}")

        db.commit()
        print("Seed completado.")
    except Exception as e:
        db.rollback()
        print(f"Error, se hizo rollback: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()