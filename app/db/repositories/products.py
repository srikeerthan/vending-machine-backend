from typing import List, Type

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.repositories.base import BaseRepository, CreateSchemaType, ModelType
from app.db.session import get_db
from app.models.products import Products
from app.schemas.products import ProductInCreate, ProductInUpdate


class ProductsRepository(BaseRepository[Products, ProductInCreate, ProductInUpdate]):
    def create_with_user(self, obj_create: ProductInCreate, user_id: int) -> ModelType:
        """
        Create new object in db table.
        """
        obj = self.model(**obj_create.dict(), creator_id=user_id)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get_product_by_name(self, product_name: str) -> Products:
        """
        Get product based on name
        :param product_name:
        :return:
        """
        product = self.db.query(Products).filter(Products.name == product_name).first()
        return product

    def get_products_by_product_ids(self, product_ids: List[int]) -> List[Products]:
        """
        Get products
        :param product_ids:
        :return:
        """
        products: List[Products] = self.db.query(Products).filter(Products.id.in_(product_ids)).all()
        return products


def get_products_repository(session: Session = Depends(get_db)) -> ProductsRepository:
    return ProductsRepository(db=session, model=Products)
