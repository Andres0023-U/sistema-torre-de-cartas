from pydantic import BaseModel

DEFAULT_DECK_NAME = "Mazo por defecto"


class DeckCreate(BaseModel):
    name: str = DEFAULT_DECK_NAME


class DeckUpdate(BaseModel):
    name: str


class DeckResponse(BaseModel):
    deck_id: int
    player_id: int
    name: str

    class Config:
        from_attributes = True