import json
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.security import get_password_hash
from app.db.base import Base


class Users(Base):
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, nullable=False)
    full_name = Column(String)
    roles = Column(String, nullable=False, default="buyer")  # Store roles as a JSON string
    hashed_password = Column(String, nullable=False)
    disabled = Column(Boolean, default=False)

    products = relationship("Products", back_populates="creator")
    deposit = relationship("Deposits", back_populates="user")

    def __init__(
            self, username: str, email: str, full_name: str, password: str, roles: list = None
    ) -> None:
        self.username = username
        self.email = email
        self.full_name = full_name
        self.roles = json.dumps(roles) if roles else json.dumps(["buyer"])  # Convert list to JSON string
        self.hashed_password = get_password_hash(password=password)
