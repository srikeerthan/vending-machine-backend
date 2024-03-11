import jwt
from fastapi import Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials, OAuth2PasswordBearer

from app.core.constants import SECRET_KEY, ALGORITHM
from app.core.exceptions import ProductNotFoundException, UserPermissionException, DepositsNotExistsException, \
    InvalidUserCredentialsException
from app.db.repositories.deposits import DepositsRepository, get_deposits_repository
from app.db.repositories.products import ProductsRepository, get_products_repository
from app.models.deposits import Deposits
from app.models.products import Products
from app.models.users import Users
from app.schemas.users import TokenData
from app.services.users import UserService

basic_security = HTTPBasic()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(
        user_service: UserService = Depends(),
        token: str = Depends(oauth2_scheme)
) -> Users:
    """
    Return current user.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise InvalidUserCredentialsException(message="Invalid Credentials. Please try again!",
                                                  status_code=status.HTTP_401_UNAUTHORIZED)
        token_data = TokenData(username=username)
    except jwt.exceptions.PyJWTError:
        raise InvalidUserCredentialsException(message="Invalid Credentials. Please try again!",
                                              status_code=status.HTTP_401_UNAUTHORIZED)
    user = user_service.user_repo.get_by_username(username=token_data.username)
    if not user or user.disabled:
        raise InvalidUserCredentialsException(
            message="Invalid Credentials. Please try again!",
            status_code=status.HTTP_401_UNAUTHORIZED,
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
    if not product or not product.is_active:
        raise ProductNotFoundException(
            message=f"Product with id `{product_id}` not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    if product.creator_id != current_user.id:
        raise UserPermissionException(
            message="You do not have permission for this product", status_code=status.HTTP_403_FORBIDDEN
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
