from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_current_user
from app.models.users import Users
from app.schemas.response import Response
from app.schemas.users import UserInDB, UserInCreate, UserToken, UserLogin, UserInUpdate
from app.services.users import UserService

router = APIRouter()


# CRUD operations for users
@router.post("", response_model=Response[UserInDB])
async def create_user(user: UserInCreate, user_service: UserService = Depends()) -> Response:
    """
    Creates a new user in the database.
    :param user:
    :param user_service:
    :return:
    """
    user = user_service.register_user(user_create=user)
    return Response(data=user, message="User Registered successfully")


@router.post("/login", response_model=Response[UserToken])
async def login_user(user: UserLogin, user_service: UserService = Depends()) -> Response:
    """
    Process user login.
    """
    token = user_service.login_user(user=user)
    return Response(data=token, message="The user authenticated successfully")


@router.get("/{username}", response_model=Response[UserInDB])
async def read_user(username: str, user: Users = Depends(get_current_user)) -> Response:
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.username != username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to access this "
                                                                          "resource")
    return Response(data=user, message="Successfully Retrieved user")


@router.put("/{username}", response_model=Response[UserInDB])
async def update_user(username: str, updated_user: UserInUpdate, current_user: Users = Depends(get_current_user),
                      user_service: UserService = Depends()) -> Response:
    user = user_service.update_user(username, updated_user, current_user)
    return Response(data=user, message="Successfully updated user")


@router.delete("/{username}", response_model=Response[UserInDB])
async def delete_user(username: str, current_user: Users = Depends(get_current_user),
                      user_service: UserService = Depends()) -> Response:
    user = user_service.delete_user(username, current_user)
    return Response(data=user, message="User deleted successfully")
