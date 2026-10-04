from pydantic import BaseModel

class DeckSelectionCreate(BaseModel):
    deck_id: int

class DeckSelectionResponse(BaseModel):
    round_deck_selection_id: int
    round_id: int
    player_id: int
    deck_id: int

    class Config:
        from_attributes = True