from typing import List

from fastapi import Depends
from sqlalchemy import select, func, desc, asc
from sqlalchemy.orm import Session

from app.core.pagination import SortEnum
from app.db.repositories.base import BaseRepository, ModelType
from app.db.session import get_db
from app.models.products import Products
from app.schemas.products import ProductInCreate, ProductInUpdate
from app.schemas.purchases import PurchaseInCreate


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

    def get_all_active_paginated_products(self, limit: int, offset: int, order: SortEnum) -> dict:
        """
        Get all active products
        :return:
        """
        order = desc if order == SortEnum.DESCENDING else asc
        with self.db as session:
            query = select(Products).filter(Products.is_active == True)
            return {
                'count': session.scalar(select(func.count()).select_from(query.subquery())),
                'products': [product for product in
                             session.scalars(query.limit(limit).offset(offset).order_by(order(Products.created_time)))]
            }

    def get_product_by_name(self, product_name: str) -> Products:
        """
        Get product based on name
        :param product_name:
        :return:
        """
        product = self.db.query(Products).filter(Products.name == product_name).first()
        return product

    def get_active_products_by_product_ids(self, product_ids: List[int]) -> List[Products]:
        """
        Get products
        :param product_ids:
        :return:
        """
        products: List[Products] = self.db.query(Products).filter(Products.id.in_(product_ids)).filter(
            Products.is_active == True).all()
        return products

    def are_active_products_exists_for_user(self, user_id: int) -> bool:
        """
        Get products
        :param user_id:
        :return:
        """
        product = self.db.query(Products).filter(Products.creator_id == user_id).filter(
            Products.is_active == True).first()
        return True if product else False

    def update_product_as_inactive(self, product_id: int) -> Products:
        product_obj = self.db.query(Products).filter(Products.id == product_id).first()
        product_obj.is_active = False
        self.db.add(product_obj)
        self.db.commit()
        self.db.refresh(product_obj)
        return product_obj

    def update_product_quantities(self, purchase: PurchaseInCreate, products_list: List[Products]) -> List[Products]:
        product_id_quantity_map = {}
        for product in purchase.products:
            product_id_quantity_map[product.product_id] = product.quantity

        for product_obj in products_list:
            purchase_quantity = product_id_quantity_map[product_obj.id]
            existing_quantity = product_obj.quantity
            new_quantity = existing_quantity - purchase_quantity if existing_quantity - purchase_quantity > 0 else 0
            setattr(product_obj, "quantity", new_quantity)
        self.db.add_all(products_list)
        self.db.commit()
        for product_obj in products_list:
            self.db.refresh(product_obj)
        return products_list


def get_products_repository(session: Session = Depends(get_db)) -> ProductsRepository:
    return ProductsRepository(db=session, model=Products)
