"""
Seed de demostración, SOLO para la base de datos local.
Uso (desde backend/ con el venv activo):
    python -m scripts.seed_demo
Crea 1 admin, 1 organizador y 8 jugadores. Todos los jugadores tienen
los mismos 2 mazos (Mazo A y Mazo B), de 20 cartas válidas.
Es idempotente: se puede correr varias veces sin duplicar datos.
"""
from sqlalchemy import text

from app.core.database import SessionLocal, engine
from app.core.security import hash_password

PASSWORD = "Demo1234"

DECKS = {
    "Mazo A": [(1, 4), (2, 3), (3, 2), (4, 1), (5, 4), (6, 3), (7, 2), (8, 1)],
    "Mazo B": [(5, 4), (6, 3), (7, 2), (8, 1), (9, 4), (10, 3), (11, 2), (12, 1)],
}

STAFF = [
    ("Administrador", "admin@demo.com", "admin"),
    ("Organizador", "organizador@demo.com", "organizer"),
]

PLAYERS = [(f"Jugador {i}", f"jugador{i}@demo.com") for i in range(1, 9)]


def role_id(db, name):
    value = db.execute(text("SELECT role_id FROM security.role WHERE name = :n"), {"n": name}).scalar()
    if value is None:
        raise RuntimeError(f"No existe el rol '{name}'. Corre primero seeds/00_roles.sql")
    return value


def get_or_create_user(db, name, email, rid, password_hash):
    row = db.execute(text('SELECT user_id FROM security."user" WHERE email = :e'), {"e": email}).first()
    if row:
        return row[0]
    return db.execute(text(
        'INSERT INTO security."user" (name, email, password_hash, role_id) '
        'VALUES (:n, :e, :p, :r) RETURNING user_id'),
        {"n": name, "e": email, "p": password_hash, "r": rid}).scalar()


def get_or_create_player(db, user_id):
    row = db.execute(text("SELECT player_id FROM players.player WHERE user_id = :u"), {"u": user_id}).first()
    if row:
        return row[0]
    return db.execute(text(
        "INSERT INTO players.player (user_id) VALUES (:u) RETURNING player_id"), {"u": user_id}).scalar()


def get_or_create_deck(db, player_id, name, cards):
    row = db.execute(text(
        "SELECT deck_id FROM players.deck WHERE player_id = :p AND name = :n"),
        {"p": player_id, "n": name}).first()
    if row:
        return row[0]
    deck_id = db.execute(text(
        "INSERT INTO players.deck (player_id, name) VALUES (:p, :n) RETURNING deck_id"),
        {"p": player_id, "n": name}).scalar()
    for card_id, qty in cards:
        db.execute(text(
            "INSERT INTO players.deck_card (deck_id, card_id, quantity) VALUES (:d, :c, :q)"),
            {"d": deck_id, "c": card_id, "q": qty})
    return deck_id


def main():
    host = engine.url.host
    if host not in ("localhost", "127.0.0.1"):
        print(f"Cancelado: el .env apunta a '{host}', no a la base local.")
        print("Ejecuta primero: ..\\switch-env.ps1 local")
        return

    for name, cards in DECKS.items():
        assert sum(q for _, q in cards) == 20, f"{name} no suma 20 cartas"

    db = SessionLocal()
    try:
        password_hash = hash_password(PASSWORD)

        for name, email, role in STAFF:
            user_id = get_or_create_user(db, name, email, role_id(db, role), password_hash)
            print(f"OK {email} ({role}): user={user_id}")

        player_rid = role_id(db, "player")
        for name, email in PLAYERS:
            user_id = get_or_create_user(db, name, email, player_rid, password_hash)
            player_id = get_or_create_player(db, user_id)
            deck_ids = [get_or_create_deck(db, player_id, d, c) for d, c in DECKS.items()]
            print(f"OK {email}: player=#{player_id} mazos={deck_ids}")

        db.commit()
        print(f"Seed de demo completado. Contraseña de todas las cuentas: {PASSWORD}")
    except Exception as e:
        db.rollback()
        print(f"Error, se hizo rollback: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()