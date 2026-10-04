from sqlalchemy import Column, Integer, String, Date, ForeignKey, TIMESTAMP, UniqueConstraint, CheckConstraint, func
from app.core.database import Base

class Tournament(Base):
    __tablename__ = "tournament"
    __table_args__ = (
        CheckConstraint("num_players > 0", name="chk_tournament_num_players"),
        {"schema": "tournaments"},
    )

    tournament_id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    date = Column(Date, nullable=False)
    format = Column(String(30), nullable=False)
    num_players = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False)
    organizer_id = Column(Integer, ForeignKey("security.user.user_id"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

class Round(Base):
    __tablename__ = "round"
    __table_args__ = (
        UniqueConstraint("tournament_id", "number", name="uq_round_tournament_number"),
        CheckConstraint("number > 0", name="chk_round_number"),
        {"schema": "tournaments"},
    )

    round_id = Column(Integer, primary_key=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.tournament.tournament_id"), nullable=False)
    number = Column(Integer, nullable=False)
    name = Column(String(30), nullable=False)
    status = Column(String(20), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

class TournamentRegistration(Base):
    __tablename__ = "tournament_registration"
    __table_args__ = (
        UniqueConstraint("tournament_id", "player_id", name="uq_tournament_registration_unique"),
        {"schema": "tournaments"},
    )

    tournament_registration_id = Column(Integer, primary_key=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.tournament.tournament_id"), nullable=False)
    player_id = Column(Integer, ForeignKey("players.player.player_id"), nullable=False)
    registered_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class RoundDeckSelection(Base):
    __tablename__ = "round_deck_selection"
    __table_args__ = (
        UniqueConstraint("round_id", "player_id", name="uq_round_deck_selection_unique"),
        {"schema": "tournaments"},
    )

    round_deck_selection_id = Column(Integer, primary_key=True)
    round_id = Column(Integer, ForeignKey("tournaments.round.round_id"), nullable=False)
    player_id = Column(Integer, ForeignKey("players.player.player_id"), nullable=False)
    deck_id = Column(Integer, ForeignKey("players.deck.deck_id"), nullable=False)
    selected_at = Column(TIMESTAMP(timezone=True), server_default=func.now())