from typing import List

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.repositories.base import BaseRepository
from app.db.session import get_db
from app.models.purchases import Purchases
from app.schemas.purchases import PurchaseInCreate, PurchaseInUpdate


class PurchasesRepository(BaseRepository[Purchases, PurchaseInCreate, PurchaseInUpdate]):
    def create_product_purchases(self, purchase: PurchaseInCreate, product_id_price_map: dict,
                                 deposit_id: int) -> List[Purchases]:
        purchase_dict = purchase.dict()
        objs_create = purchase_dict.get("products")
        for obj in objs_create:
            product_quantity = obj.get("quantity")
            product_id = obj.get("product_id")
            product_price = product_id_price_map.get(product_id)
            obj["total_spent"] = round(product_quantity * product_price, 2)
            obj["deposit_id"] = deposit_id
        purchases_objs = [Purchases(**data) for data in objs_create]
        self.db.add_all(purchases_objs)
        self.db.commit()
        for purchase_obj in purchases_objs:
            self.db.refresh(purchase_obj)
        return purchases_objs

    def are_purchases_exists_for_product(self, product_id: int) -> bool:
        purchases = self.db.query(Purchases).filter(Purchases.product_id == product_id).first()
        return True if purchases else False


def get_purchases_repository(session: Session = Depends(get_db)) -> PurchasesRepository:
    return PurchasesRepository(db=session, model=Purchases)
