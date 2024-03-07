import json

from sqlalchemy import Column, Integer, Numeric, ForeignKey, DateTime, func, String, Boolean
from sqlalchemy.orm import relationship

from app.db.base import Base


class Deposits(Base):
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    amount = Column(Numeric(11, 2), nullable=False)
    coins = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    is_deposit_utilized = Column(Boolean, default=False)

    # Relationships
    purchases = relationship("Purchases", back_populates="deposit")
    user = relationship("Users", back_populates="deposit")

    created_time = Column(DateTime, default=func.now())
    updated_time = Column(DateTime, default=func.now(), onupdate=func.now())

    def __init__(self, amount: float, coins: list, user_id: int):
        self.amount = amount
        self.coins = json.dumps(coins)
        self.user_id = user_id
