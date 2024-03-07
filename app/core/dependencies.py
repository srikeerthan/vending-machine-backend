from fastapi import Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.core.exceptions import ProductNotFoundException, UserPermissionException, DepositsNotExistsException
from app.db.repositories.deposits import DepositsRepository, get_deposits_repository
from app.db.repositories.products import ProductsRepository, get_products_repository
from app.models.deposits import Deposits
from app.models.products import Products
from app.models.users import Users
from app.services.users import UserService

basic_security = HTTPBasic()


def get_current_user(
        user_service: UserService = Depends(),
        credentials: HTTPBasicCredentials = Depends(basic_security),
) -> Users:
    """
    Return current user.
    """
    user = user_service.authenticate(
        username=credentials.username, password=credentials.password
    )
    return user


def get_current_product(product_id: int,
                        products_repo: ProductsRepository = Depends(get_products_repository),
                        current_user: Users = Depends(get_current_user)) -> Products:
    """
    Return current product
    :return:
    """
    product = products_repo.get(product_id)
    if not product:
        raise ProductNotFoundException(
            message=f"Product with id `{product_id}` not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    if product.creator_id != current_user.id:
        raise UserPermissionException(
            message="Not enough permissions", status_code=status.HTTP_403_FORBIDDEN
        )
    return product


def get_current_deposit(current_user: Users = Depends(get_current_user),
                        deposits_repo: DepositsRepository = Depends(get_deposits_repository)) -> Deposits:
    """
    Returns current not utilized deposit of current user.
    :param current_user:
    :param deposits_repo:
    :return:
    """
    deposit = deposits_repo.get_not_utilized_deposits_by_user(current_user.id)
    if not deposit:
        raise DepositsNotExistsException(message="Deposits not found", status_code=status.HTTP_404_NOT_FOUND)
    return deposit

# def get_current_active_user(
#     user_service: UserService = Depends(),
#     current_user: User = Depends(get_current_user),
# ) -> User:
#     """
#     Return current active user.
#     """
#     if not user_service.check_is_active(user=current_user):
#         raise InactiveUserAccountException(
#             message="Inactive user", status_code=HTTP_400_BAD_REQUEST
#         )
#     return current_user
