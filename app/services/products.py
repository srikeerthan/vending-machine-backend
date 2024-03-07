from typing import List

from fastapi import Depends, status

from app.core.exceptions import UserPermissionException, ProductAlreadyExistsException
from app.core.logging import logger
from app.db.repositories.products import ProductsRepository, get_products_repository
from app.models.products import Products
from app.models.users import Users
from app.schemas.products import ProductInCreate, ProductInUpdate


class ProductsService:
    def __init__(
            self, products_repo: ProductsRepository = Depends(get_products_repository)
    ) -> None:
        self.products_repo = products_repo

    @staticmethod
    def is_current_user_seller(current_user: Users) -> bool:
        return "seller" in current_user.roles

    def handle_product_with_same_name(self, product_name: str) -> None:
        logger.info(f"Try to find product: {product_name}")
        product = self.products_repo.get_product_by_name(product_name=product_name)
        if product:
            raise ProductAlreadyExistsException(message=f"Product with name: `{product_name}` already exists",
                                                status_code=status.HTTP_400_BAD_REQUEST)

    def create_product(self, product_create: ProductInCreate, current_user: Users) -> Products:
        if not self.is_current_user_seller(current_user):
            raise UserPermissionException(message="Only seller can create products",
                                          status_code=status.HTTP_403_FORBIDDEN)
        self.handle_product_with_same_name(product_create.name)
        product = self.products_repo.create_with_user(product_create, current_user.id)
        return product

    def get_all_products(self) -> List[Products]:
        products = self.products_repo.get_all()
        return products

    def update_product(self, product_in_update: ProductInUpdate, current_product: Products) -> Products:
        if product_in_update.name != current_product.name:
            self.handle_product_with_same_name(product_in_update.name)
        return self.products_repo.update(obj=current_product, obj_update=product_in_update)

    def delete_product(self, product: Products) -> Products:
        # TODO: handle products relations with other tables
        return self.products_repo.delete(product.id)
