from pydantic import BaseModel

class DeckCardCreate(BaseModel):
    card_id: int
    quantity: int = 1

class DeckCardResponse(BaseModel):
    deck_id: int
    card_id: int
    quantity: int

    class Config:
        from_attributes = True