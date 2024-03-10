from typing import List

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.repositories.base import BaseRepository, ModelType, UpdateSchemaType
from app.db.session import get_db
from app.models.deposits import Deposits
from app.schemas.deposits import DepositInCreate, DepositInUpdate


class DepositsRepository(BaseRepository[Deposits, DepositInCreate, DepositInUpdate]):

    def get_not_utilized_deposits_by_user(self, user_id) -> Deposits:
        deposit = self.db.query(Deposits).filter(Deposits.user_id == user_id).filter(
            Deposits.is_deposit_utilized == False).first()
        return deposit

    def are_deposits_exists_for_user(self, user_id) -> bool:
        deposit = self.db.query(Deposits).filter(Deposits.user_id == user_id).first()
        return True if deposit else False

    def create_deposit_with_total_amount(self, obj_create: DepositInCreate, user_id: int,
                                         total_amount: float) -> ModelType:
        obj = self.model(**obj_create.dict(), user_id=user_id, amount=total_amount)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update_deposit_as_utilized(self, deposit_id: int) -> Deposits:
        obj = self.db.query(self.model).get(deposit_id)
        setattr(obj, "is_deposit_utilized", True)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj


def get_deposits_repository(session: Session = Depends(get_db)) -> DepositsRepository:
    return DepositsRepository(db=session, model=Deposits)
