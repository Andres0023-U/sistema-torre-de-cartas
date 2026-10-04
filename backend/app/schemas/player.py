from pydantic import BaseModel

class PlayerResponse(BaseModel):
    player_id: int
    user_id: int

    class Config:
        from_attributes = True

class PlayerWithUserResponse(BaseModel):
    player_id: int
    user_id: int
    name: str
    email: str