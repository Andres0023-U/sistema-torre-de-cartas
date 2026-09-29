from sqlalchemy import Column, Integer, String, CheckConstraint
from app.core.database import Base

class Card(Base):
    __tablename__ = "card"
    __table_args__ = (
        CheckConstraint("value >= 0", name="chk_card_value"),
        CheckConstraint("max_quantity > 0", name="chk_card_max_quantity"),
        {"schema": "cards"},
    )

    card_id = Column(Integer, primary_key=True)
    card_name = Column(String(100), nullable=False, unique=True)
    value = Column(Integer, nullable=False)
    type = Column(String(20), nullable=False)
    effect = Column(String(255))
    max_quantity = Column(Integer, nullable=False)
    rarity = Column(String(20), nullable=False)
    description = Column(String(255), nullable=False)