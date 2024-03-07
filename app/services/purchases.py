from typing import List

from fastapi import Depends, status
from pydantic import parse_obj_as

from app.core.exceptions import InvalidInputDataException
from app.db.repositories.deposits import DepositsRepository, get_deposits_repository
from app.db.repositories.products import ProductsRepository, get_products_repository
from app.db.repositories.purchases import get_purchases_repository, PurchasesRepository
from app.models.deposits import Deposits
from app.models.products import Products
from app.models.purchases import Purchases
from app.schemas.purchases import PurchaseInCreate, PurchaseResponse, PurchaseItem


class PurchasesService:
    def __init__(
            self, purchases_repo: PurchasesRepository = Depends(get_purchases_repository),
            products_repo: ProductsRepository = Depends(get_products_repository),
            deposits_repo: DepositsRepository = Depends(get_deposits_repository)
    ) -> None:
        self.purchases_repo = purchases_repo
        self.products_repo = products_repo
        self.deposits_repo = deposits_repo

    def handle_products(self, products: List[PurchaseItem],
                        deposit_amount: float) -> tuple[List[Products], float, dict]:
        product_ids = {product_item.product_id for product_item in products}
        products_list = self.products_repo.get_products_by_product_ids(list(product_ids))
        if len(products_list) != len(product_ids):
            raise InvalidInputDataException(message="some of the provided product ids not exists",
                                            status_code=status.HTTP_400_BAD_REQUEST)
        product_id_price_map, product_id_quantity_map = {}, {}
        for product in products_list:
            product_id_price_map[product.id] = product.price
            product_id_quantity_map[product.id] = product.quantity
        products_amount = 0
        for product_item in products:
            product_id = product_item.product_id
            product_quantity = product_item.quantity
            if product_quantity < 0 or product_quantity > product_id_quantity_map.get(product_id):
                raise InvalidInputDataException(message=f"Invalid quantity passed for product_id: {product_id}, "
                                                        f"available quantity: {product_id_quantity_map.get(product_id)}",
                                                status_code=status.HTTP_400_BAD_REQUEST)
            products_amount += (product_id_price_map[product_id] * product_quantity)

        if products_amount > deposit_amount:
            raise InvalidInputDataException(
                message=f"The deposited Amount: ${deposit_amount} is less than selected products "
                        f"amount: ${products_amount}",
                status_code=status.HTTP_400_BAD_REQUEST)
        remaining_change = round(deposit_amount - products_amount, 2)
        return products_list, remaining_change, product_id_price_map

    @staticmethod
    def get_remaining_coin_count(remaining_change: float):
        """
        Returns the remaining change in the form of coin count
        :param remaining_change:
        :return:
        """
        remaining_change_in_cents = remaining_change * 100
        allowed_coins = [100, 50, 20, 10, 5]
        coin_count = []

        for coin in allowed_coins:
            count = remaining_change_in_cents // coin
            if count > 0:
                coin_count.append({"value": coin, "quantity": count})
                remaining_change_in_cents %= coin

        return coin_count

    def buy_products(self, purchase: PurchaseInCreate, current_deposit: Deposits) -> PurchaseResponse:
        products_list, remaining_change, product_id_price_map = self.handle_products(purchase.products,
                                                                                     current_deposit.amount)
        self.purchases_repo.create_product_purchases(purchase, product_id_price_map, current_deposit.id)
        self.deposits_repo.update_deposit_as_utilized(current_deposit.id)
        result_json = purchase.dict(exclude_unset=True)
        result_json['total_spent'] = round(current_deposit.amount - remaining_change, 2) * 100
        remaining_change_coins = self.get_remaining_coin_count(remaining_change)
        result_json["change"] = remaining_change_coins
        purchase_response = parse_obj_as(PurchaseResponse, result_json)
        return purchase_response
