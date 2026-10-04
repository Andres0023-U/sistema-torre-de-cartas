from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user_payload
from app.schemas.card import CardResponse
from app.models.cards import Card

router = APIRouter(prefix="/cards", tags=["cards"])

@router.get("/", response_model=list[CardResponse])
def list_cards(
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user_payload)
):
    return db.query(Card).all()