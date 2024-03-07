from sqlalchemy import Column, BigInteger, String, Numeric, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class Products(Base):
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    name = Column(String, unique=True, index=True, nullable=False)
    price = Column(Numeric(11, 2), nullable=False)
    quantity = Column(Integer, nullable=False)

    # Establishing many-to-one relationship with User
    creator_id = Column(Integer, ForeignKey('users.id'))
    creator = relationship("Users", back_populates="products")

    created_time = Column(DateTime, default=func.now())
    updated_time = Column(DateTime, default=func.now(), onupdate=func.now())

    def __init__(
            self, name: str, price: float, quantity: int, creator_id: int
    ) -> None:
        self.name = name
        self.price = price
        self.quantity = quantity
        self.creator_id = creator_id
