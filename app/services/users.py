from http import HTTPStatus
from typing import Optional

from fastapi import Depends, HTTPException, status

from app.core.exceptions import UserAlreadyExistException, UserNotFoundException, InvalidUserCredentialsException, \
    InvalidRolesException, UserPermissionException
from app.core.logging import logger
from app.core.security import verify_password, get_basic_auth_token
from app.db.repositories.users import UsersRepository, get_users_repository
from app.models.users import Users
from app.schemas.users import UserInCreate, UserLogin, UserToken, UserInUpdate


class UserService:
    def __init__(
            self, user_repo: UsersRepository = Depends(get_users_repository)
    ) -> None:
        self.user_repo = user_repo

    def login_user(self, user: UserLogin) -> UserToken:
        """
        Authenticate user with provided credentials.
        """
        logger.info(f"Try to login user: {user.username}")
        self.authenticate(username=user.username, password=user.password)
        return UserToken(
            token=get_basic_auth_token(username=user.username, password=user.password)
        )

    def validate_roles(self, roles: list) -> list:
        allowed_roles = {"seller", "buyer"}
        for role in roles:
            if role not in allowed_roles:
                raise InvalidRolesException(
                    message=f"Invalid role: {role}. Allowed roles are: {', '.join(allowed_roles)}",
                    status_code=status.HTTP_400_BAD_REQUEST)
        return roles

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
        self.validate_roles(user_create.roles)
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
        self.validate_roles(user_in_update.roles)
        # TODO: handle changing roles from sellers to buyers and handle products

        user = self.user_repo.update(obj=current_user, obj_update=user_in_update)
        return user

    def delete_user(self, username: str, current_user: Users) -> Users:
        if current_user.username != username:
            raise UserPermissionException(status_code=status.HTTP_403_FORBIDDEN,
                                          message="You don't have permission to access this resource")
        # TODO: handle deletion of users with products and transactions attached
        return self.user_repo.delete(current_user.id)

    def authenticate(self, username: str, password: str) -> Users:
        """
        Authenticate user.
        """
        logger.info(f"Try to authenticate user: {username}")
        user = self.user_repo.get_by_username(username=username)
        if not user:
            raise UserNotFoundException(
                message=f"User with username: `{username}` not found",
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
