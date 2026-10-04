from pydantic import BaseModel

class DeckCreate(BaseModel):
    name: str = "Mazo"

class DeckResponse(BaseModel):
    deck_id: int
    player_id: int
    name: str

    class Config:
        from_attributes = True