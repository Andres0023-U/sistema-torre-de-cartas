from pydantic import BaseModel

class CardResponse(BaseModel):
    card_id: int
    card_name: str
    value: int
    type: str
    effect: str | None
    max_quantity: int
    rarity: str
    description: str

    class Config:
        from_attributes = True