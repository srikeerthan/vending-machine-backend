from typing import List

from fastapi import Depends, status
from pydantic import parse_obj_as

from app.core.exceptions import UserPermissionException, DepositsAlreadyExistsException
from app.core.user_roles_enum import UserRoles
from app.db.repositories.deposits import DepositsRepository, get_deposits_repository
from app.db.utils import model_to_dict
from app.models.deposits import Deposits
from app.models.users import Users
from app.schemas.deposits import DepositInCreate, DepositsResponse, CoinsItem


class DepositsService:
    def __init__(
            self, deposits_repo: DepositsRepository = Depends(get_deposits_repository)
    ) -> None:
        self.deposits_repo = deposits_repo

    @staticmethod
    def is_current_user_buyer(user: Users) -> bool:
        return UserRoles.BUYER_ROLE.value in user.roles

    def handle_not_utilized_deposits(self, user: Users) -> None:
        """
        Handles not utilized deposits exists for the current user and raises an exception
        :param user:
        :return:
        """
        not_utilized_deposit = self.deposits_repo.get_not_utilized_deposits_by_user(user.id)
        if not_utilized_deposit:
            raise DepositsAlreadyExistsException(message=f"Deposits already exists for user {user.username}",
                                                 status_code=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_total_deposit_amount(coins: List[CoinsItem]) -> float:
        total_amount_in_cents = 0
        for coin_item in coins:
            total_amount_in_cents += coin_item.value * coin_item.quantity
        total_amount_in_dollars = round(total_amount_in_cents / 100.0, 2)
        return total_amount_in_dollars

    def create_deposit(self, deposit_in_create: DepositInCreate, current_user: Users) -> DepositsResponse:
        """
        Creates a new deposit for the current user
        :param deposit_in_create:
        :param current_user:
        :return:
        """
        if not self.is_current_user_buyer(current_user):
            raise UserPermissionException(message="Only users with buyer permission can deposit",
                                          status_code=status.HTTP_403_FORBIDDEN)
        self.handle_not_utilized_deposits(current_user)
        total_deposit_amount = self.get_total_deposit_amount(deposit_in_create.coins)
        deposit_obj = self.deposits_repo.create_deposit_with_total_amount(deposit_in_create, current_user.id,
                                                                          total_deposit_amount)
        deposit_dict = model_to_dict(deposit_obj)
        deposit_dict["total_deposit_amount"] = total_deposit_amount
        deposit = parse_obj_as(DepositsResponse, deposit_dict)
        return deposit

    def reset_deposit(self, deposit: Deposits) -> Deposits:
        """
        Resets/Deletes the existing deposit
        :param deposit:
        :return:
        """
        deposit = self.deposits_repo.delete(deposit.id)
        return deposit
