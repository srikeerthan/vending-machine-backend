import json
from typing import Optional, List

from fastapi import status
from pydantic import ConfigDict, BaseModel, EmailStr, field_validator, Field, model_validator

from app.core.constants import ALLOWED_USER_ROLES
from app.core.exceptions import InvalidInputDataException


class User(BaseModel):
    username: str = Field(description="Username", strict=True, max_length=20)
    email: EmailStr = Field(description="Email of user")
    full_name: str = Field(description="Full name of user", max_length=49)
    roles: List[str] = Field(description="roles of user")

    @field_validator('username')
    def convert_to_lowercase(cls, v):
        return v.lower()


class UserLogin(BaseModel):
    username: str = Field(description="Username", strict=True, max_length=20)
    password: str = Field(description="Password of user", strip=True, strict=True, max_length=25)
    model_config = ConfigDict(json_schema_extra={"example": {"username": "user", "password": "weak_password"}})

    @field_validator('username')
    def convert_to_lowercase(cls, v):
        return v.lower()


class UserInCreate(User):
    password: str = Field(description="Password of user", strip=True, strict=True, max_length=25)

    @field_validator('roles')
    def validate_roles(cls, v):
        if not v or len(v) > len(ALLOWED_USER_ROLES):
            raise InvalidInputDataException(
                message=f"Invalid role provided. Allowed roles are: {ALLOWED_USER_ROLES}",
                status_code=status.HTTP_400_BAD_REQUEST)
        for role in v:
            if role not in ALLOWED_USER_ROLES:
                raise InvalidInputDataException(
                    message=f"Invalid role provided. Allowed roles are: {ALLOWED_USER_ROLES}",
                    status_code=status.HTTP_400_BAD_REQUEST)
        return v

    class Config:
        json_schema_extra = {
            "example": {"username": "ram", "email": "ram@gmail.com", "full_name": "Ram Reddy", "roles": ["seller"],
                        "password": "<STRONG_PASSWORD>"}}


class UserInUpdate(User):
    username: Optional[str] = Field(None, description="Username", strict=True, max_length=20)
    email: Optional[EmailStr] = Field(None, description="Email of user")
    full_name: Optional[str] = Field(None, description="Full name of user", max_length=49)
    roles: Optional[list] = Field([], description="roles of user")
    password: Optional[str] = None

    @field_validator('username')
    def convert_to_lowercase(cls, v):
        return v.lower()

    @field_validator('roles')
    def validate_roles(cls, v):
        if not v or len(v) > len(ALLOWED_USER_ROLES):
            raise InvalidInputDataException(
                message=f"Invalid role provided. Allowed roles are: {ALLOWED_USER_ROLES}",
                status_code=status.HTTP_400_BAD_REQUEST)
        for role in v:
            if role not in ALLOWED_USER_ROLES:
                raise InvalidInputDataException(
                    message=f"Invalid role provided. Allowed roles are: {ALLOWED_USER_ROLES}",
                    status_code=status.HTTP_400_BAD_REQUEST)
        return v

    @model_validator(mode="after")
    def check_at_least_one_field_present(self) -> 'UserInUpdate':
        if not (self.username or self.email or self.full_name or self.roles or self.password):
            raise InvalidInputDataException(
                message="At least one field (name, price, quantity) must be specified for update",
                status_code=status.HTTP_400_BAD_REQUEST)
        return self


class UserInDB(User):
    id: int

    @field_validator('roles', mode="before")
    def convert_roles_to_list(cls, v) -> list:
        if isinstance(v, str):
            return json.loads(v)
        return v

    class Config:
        json_schema_extra = {
            "example": {"id": 10343, "username": "ram", "email": "ram@gmail.com", "full_name": "Ram Reddy",
                        "roles": ["seller"]}}


class UserToken(BaseModel):
    token: str
