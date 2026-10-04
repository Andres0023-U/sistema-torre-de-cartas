from pydantic import BaseModel

class PlayerResponse(BaseModel):
    player_id: int
    user_id: int

    class Config:
        from_attributes = True