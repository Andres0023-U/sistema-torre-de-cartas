from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Player(Base):
    __tablename__ = "player"
    __table_args__ = {"schema": "players"}

    player_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("security.user.user_id"), nullable=False, unique=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

class Deck(Base):
    __tablename__ = "deck"
    __table_args__ = {"schema": "players"}

    deck_id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("players.player.player_id"), nullable=False)
    name = Column(String(50), nullable=False, default="Mazo")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

class DeckCard(Base):
    __tablename__ = "deck_card"
    __table_args__ = {"schema": "players"}

    deck_id = Column(Integer, ForeignKey("players.deck.deck_id"), primary_key=True)
    card_id = Column(Integer, ForeignKey("cards.card.card_id"), primary_key=True)