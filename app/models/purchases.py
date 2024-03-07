from sqlalchemy import Column, Integer, ForeignKey, Numeric, DateTime, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class Purchases(Base):
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    deposit_id = Column(Integer, ForeignKey('deposits.id'))
    quantity = Column(Integer, nullable=False)
    total_spent = Column(Numeric(11, 2), nullable=False)

    # Relationships
    deposit = relationship("Deposits", back_populates="purchases")
    product = relationship("Products")

    created_time = Column(DateTime, default=func.now())
    updated_time = Column(DateTime, default=func.now(), onupdate=func.now())

    def __init__(self, product_id: int, quantity: int, total_spent: float, deposit_id: int):
        self.product_id = product_id
        self.quantity = quantity
        self.total_spent = total_spent
        self.deposit_id = deposit_id
