from pydantic import BaseModel

class RegistrationCreate(BaseModel):
    player_id: int

class RegistrationResponse(BaseModel):
    tournament_registration_id: int
    tournament_id: int
    player_id: int

    class Config:
        from_attributes = True

class DeckSelectionCreate(BaseModel):
    deck_id: int

class DeckSelectionResponse(BaseModel):
    round_deck_selection_id: int
    round_id: int
    player_id: int
    deck_id: int

    class Config:
        from_attributes = True