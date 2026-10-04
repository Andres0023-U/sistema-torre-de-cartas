from pydantic import BaseModel
from datetime import date
from typing import Literal

class TournamentCreate(BaseModel):
    name: str
    date: date
    format: str
    num_players: Literal[4, 8, 16, 32]

class TournamentResponse(BaseModel):
    tournament_id: int
    name: str
    date: date
    format: str
    num_players: int
    status: str
    organizer_id: int

    class Config:
        from_attributes = True