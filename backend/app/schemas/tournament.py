from pydantic import BaseModel
from datetime import date

class TournamentCreate(BaseModel):
    name: str
    date: date
    format: str
    num_players: int

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