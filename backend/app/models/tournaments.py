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