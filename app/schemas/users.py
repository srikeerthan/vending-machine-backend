import json
from typing import Optional

from fastapi import status
from pydantic import ConfigDict, BaseModel, EmailStr, field_validator

from app.core.exceptions import InvalidInputDataException


class User(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    roles: list

    @field_validator('roles', mode='before')
    def convert_roles_to_list(cls, v) -> list:
        if isinstance(v, str):
            return json.loads(v)
        return v


class UserLogin(BaseModel):
    username: str
    password: str
    model_config = ConfigDict(json_schema_extra={"example": {"username": "user", "password": "weak_password"}})


class UserInCreate(User):
    password: str


class UserInUpdate(User):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    roles: Optional[list] = []
    password: Optional[str] = None

    @field_validator('username', 'email', 'full_name', 'roles', 'password', mode='before')
    def at_least_one_field_required(cls, v, values):
        provided_values = [value for value in values.values() if value]
        if not provided_values:
            raise InvalidInputDataException(message="At least one field is required",
                                            status_code=status.HTTP_400_BAD_REQUEST)
        return v


class UserInDB(User):
    model_config = ConfigDict(from_attributes=True)


class UserToken(BaseModel):
    token: str
