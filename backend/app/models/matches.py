from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, CheckConstraint, func
from app.core.database import Base

class Match(Base):
    __tablename__ = "match"
    __table_args__ = (
        CheckConstraint("deck1_id <> deck2_id", name="chk_match_different_decks"),
        {"schema": "matches"},
    )

    match_id = Column(Integer, primary_key=True)
    round_id = Column(Integer, ForeignKey("tournaments.round.round_id"), nullable=False)
    deck1_id = Column(Integer, ForeignKey("players.deck.deck_id"), nullable=False)
    deck2_id = Column(Integer, ForeignKey("players.deck.deck_id"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

class Result(Base):
    __tablename__ = "result"
    __table_args__ = {"schema": "matches"}

    result_id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("matches.match.match_id"), nullable=False, unique=True)
    winner_id = Column(Integer, ForeignKey("players.deck.deck_id"), nullable=False)
    end_phase = Column(String(20), nullable=False)
    player1_final_life = Column(Integer, nullable=False)
    player2_final_life = Column(Integer, nullable=False)
    player1_points = Column(Integer, nullable=False)
    player2_points = Column(Integer, nullable=False)
    date = Column(TIMESTAMP(timezone=True), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

class MatchDeckCard(Base):
    __tablename__ = "match_deck_card"
    __table_args__ = (
        CheckConstraint("player_slot IN (1, 2)", name="chk_match_deck_card_slot"),
        {"schema": "matches"},
    )

    match_deck_card_id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("matches.match.match_id"), nullable=False)
    card_id = Column(Integer, ForeignKey("cards.card.card_id"), nullable=False)
    player_slot = Column(Integer, nullable=False)
    state = Column(String(20), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

class MatchPlayerState(Base):
    __tablename__ = "match_player_state"
    __table_args__ = (
        CheckConstraint("player_slot IN (1, 2)", name="chk_match_player_state_slot"),
        {"schema": "matches"},
    )

    match_id = Column(Integer, ForeignKey("matches.match.match_id"), primary_key=True)
    player_slot = Column(Integer, primary_key=True)
    current_life = Column(Integer)
    current_shield = Column(Integer)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())