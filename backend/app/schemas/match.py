from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class MatchCreate(BaseModel):
    round_id: int
    deck1_id: int
    deck2_id: int

class MatchResponse(BaseModel):
    match_id: int
    round_id: int
    deck1_id: int
    deck2_id: int

    class Config:
        from_attributes = True

class ResultCreate(BaseModel):
    winner_id: int          # deck_id del ganador
    end_phase: str           # 'normal' u 'overtime'
    player1_final_life: int
    player2_final_life: int
    duration_minutes: Optional[int] = Field(None, ge=1, le=600)
    date: Optional[datetime] = None

class ResultResponse(BaseModel):
    result_id: int
    match_id: int
    winner_id: int
    end_phase: str
    player1_final_life: int
    player2_final_life: int
    player1_points: int
    player2_points: int
    date: datetime
    duration_minutes: Optional[int] = None

    class Config:
        from_attributes = True