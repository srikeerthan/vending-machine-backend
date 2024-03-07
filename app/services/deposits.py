from fastapi import Depends, status

from app.core.exceptions import UserPermissionException, DepositsAlreadyExistsException
from app.db.repositories.deposits import DepositsRepository, get_deposits_repository
from app.models.deposits import Deposits
from app.models.users import Users
from app.schemas.deposits import DepositInCreate


class DepositsService:
    def __init__(
            self, deposits_repo: DepositsRepository = Depends(get_deposits_repository)
    ) -> None:
        self.deposits_repo = deposits_repo

    @staticmethod
    def is_current_user_buyer(user: Users) -> bool:
        return "buyer" in user.roles

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
    def get_total_deposit_amount(coins: list) -> float:
        total_amount_in_cents = 0
        for coin_dict in coins:
            total_amount_in_cents += coin_dict["value"] * coin_dict["quantity"]
        total_amount_in_dollars = round(total_amount_in_cents / 100.0, 2)
        return total_amount_in_dollars

    def create_deposit(self, deposit: DepositInCreate, current_user: Users) -> Deposits:
        """
        Creates a new deposit for the current user
        :param deposit:
        :param current_user:
        :return:
        """
        if not self.is_current_user_buyer(current_user):
            raise UserPermissionException(message="Only users with buyer permission can deposit",
                                          status_code=status.HTTP_403_FORBIDDEN)
        self.handle_not_utilized_deposits(current_user)
        total_deposit_amount = self.get_total_deposit_amount(deposit.coins)
        deposit = self.deposits_repo.create_deposit_with_total_amount(deposit, current_user.id, total_deposit_amount)
        return deposit

    def reset_deposit(self, deposit: Deposits) -> Deposits:
        """
        Resets/Deletes the existing deposit
        :param deposit:
        :return:
        """
        deposit = self.deposits_repo.delete(deposit.id)
        return deposit
