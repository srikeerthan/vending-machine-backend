import json
from http import HTTPStatus

from fastapi import Depends, status

from app.core.exceptions import UserAlreadyExistException, UserNotFoundException, InvalidUserCredentialsException, \
    InvalidRolesException, UserPermissionException, ActiveDepositsExistsException
from app.core.logging import logger
from app.core.security import verify_password, get_basic_auth_token
from app.core.user_roles_enum import UserRoles
from app.db.repositories.deposits import DepositsRepository, get_deposits_repository
from app.db.repositories.products import ProductsRepository, get_products_repository
from app.db.repositories.users import UsersRepository, get_users_repository
from app.models.users import Users
from app.schemas.users import UserInCreate, UserLogin, UserToken, UserInUpdate


class UserService:
    def __init__(
            self, user_repo: UsersRepository = Depends(get_users_repository),
            products_repo: ProductsRepository = Depends(get_products_repository),
            deposits_repo: DepositsRepository = Depends(get_deposits_repository)
    ) -> None:
        self.user_repo = user_repo
        self.products_repo = products_repo
        self.depositions_repo = deposits_repo

    def login_user(self, user: UserLogin) -> UserToken:
        """
        Authenticate user with provided credentials.
        """
        logger.info(f"Try to login user: {user.username}")
        self.authenticate(username=user.username, password=user.password)
        return UserToken(
            token=get_basic_auth_token(username=user.username, password=user.password)
        )

    def handle_roles_update(self, user_id: int, new_roles: list, current_roles: str) -> None:
        current_roles = json.loads(current_roles)
        if UserRoles.SELLER_ROLE.value in current_roles and UserRoles.SELLER_ROLE.value not in new_roles:
            if self.products_repo.are_active_products_exists_for_user(user_id):
                raise InvalidRolesException(
                    message="You cannot remove seller role as there are products present under your account",
                    status_code=status.HTTP_400_BAD_REQUEST)
        if UserRoles.BUYER_ROLE.value in current_roles and UserRoles.BUYER_ROLE.value not in new_roles:
            if self.depositions_repo.get_not_utilized_deposits_by_user(user_id):
                raise InvalidRolesException(
                    message="You cannot remove buyer role as there are active deposits exists under your account",
                    status_code=status.HTTP_400_BAD_REQUEST)

    def register_user(self, user_create: UserInCreate) -> Users:
        """
        Register user in application.
        """
        logger.info(f"Try to find user: {user_create.username}")
        db_user = self.user_repo.get_by_username(username=user_create.username)
        if db_user:
            raise UserAlreadyExistException(
                message=f"User with username: `{user_create.username}` already exists",
                status_code=HTTPStatus.UNAUTHORIZED,
            )
        logger.info(f"Creating user: {user_create.username}")
        user = self.user_repo.create(obj_create=user_create)
        return user

    def update_user(self, username: str, user_in_update: UserInUpdate, current_user: Users) -> Users:
        if current_user.username != username:
            raise UserPermissionException(status_code=status.HTTP_403_FORBIDDEN,
                                          message="You don't have permission to access this resource")
        if current_user.username != user_in_update.username:
            db_user = self.user_repo.get_by_username(username=user_in_update.username)
            if db_user:
                raise UserAlreadyExistException(
                    message=f"User with username: `{user_in_update.username}` already exists",
                    status_code=HTTPStatus.UNAUTHORIZED,
                )
        self.handle_roles_update(current_user.id, user_in_update.roles, current_user.roles)

        user = self.user_repo.update(obj=current_user, obj_update=user_in_update)
        return user

    def delete_user(self, username: str, current_user: Users) -> Users:
        if current_user.username != username:
            raise UserPermissionException(status_code=status.HTTP_403_FORBIDDEN,
                                          message="You don't have permission to access this resource")
        current_user_roles = json.loads(current_user.roles)
        if UserRoles.SELLER_ROLE.value in current_user_roles and self.products_repo.are_active_products_exists_for_user(
                current_user.id):
            return self.user_repo.disable_user(current_user)
        if UserRoles.BUYER_ROLE.value in current_user_roles and self.depositions_repo.are_deposits_exists_for_user(
                current_user.id):
            if self.depositions_repo.get_not_utilized_deposits_by_user(current_user.id):
                raise ActiveDepositsExistsException(
                    message="There active deposits exists under your account. Kindly reset or utilize the deposits "
                            "before proceeding for deletion of your account", status_code=status.HTTP_400_BAD_REQUEST)
            return self.user_repo.disable_user(current_user)
        return self.user_repo.delete(current_user.id)

    def authenticate(self, username: str, password: str) -> Users:
        """
        Authenticate user.
        """
        logger.info(f"Try to authenticate user: {username}")
        user = self.user_repo.get_by_username(username=username)
        if not user or user.disabled:
            raise InvalidUserCredentialsException(
                message=f"Invalid Credentials. Please try again",
                status_code=HTTPStatus.UNAUTHORIZED,
            )
        if not verify_password(
                plain_password=password, hashed_password=user.hashed_password
        ):
            raise InvalidUserCredentialsException(
                message="Invalid credentials", status_code=HTTPStatus.UNAUTHORIZED
            )
        return user

    def check_is_active(self, user: Users) -> bool:
        """
        Check if user account is active.
        """
        return self.user_repo.is_active(user=user)
