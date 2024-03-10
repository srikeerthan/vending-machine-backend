import json

from fastapi import status
from pydantic import BaseModel, Field, field_validator

from app.core.constants import ALLOWED_CENT_COINS
from app.core.exceptions import InvalidCentCoinException


class CoinsItem(BaseModel):
    value: int = Field(strict=True, gt=0)
    quantity: int = Field(strict=True, gt=0)

    @field_validator("value", mode='before')
    def validate_value(cls, v) -> int:
        if v not in ALLOWED_CENT_COINS:
            raise InvalidCentCoinException(message=f"'value' must be one of {ALLOWED_CENT_COINS}",
                                           status_code=status.HTTP_400_BAD_REQUEST)
        return v

    @classmethod
    def from_dict(cls, d):
        return cls(**d)


class Deposits(BaseModel):
    coins: list[CoinsItem] = Field(default_factory=list,
                                   title="List of dicts containing coins value as key and quantity as value",
                                   json_schema_extra={
                                       "example": [{"value": 5, "quantity": 10}, {"value": 10, "quantity": 5},
                                                   {"value": 20, "quantity": 3}, {"value": 50, "quantity": 2},
                                                   {"value": 100, "quantity": 1}]}
                                   )

    @field_validator('coins', mode='before')
    def convert_coins_to_list(cls, v) -> list:
        if isinstance(v, str):
            coins_list = json.loads(v)
            coins_items = [CoinsItem.from_dict(coin_dict) for coin_dict in coins_list]
            return coins_items
        return v


class DepositInCreate(Deposits):
    ...


class DepositInUpdate(Deposits):
    ...


class DepositResetResponse(BaseModel):
    ...


class DepositsResponse(Deposits):
    total_deposit_amount: float

    class Config:
        json_schema_extra = {"example": {"total_deposit_amount": 1.50,
                                         "coins": [{"value": 5, "quantity": 10}, {"value": 10, "quantity": 5},
                                                   {"value": 20, "quantity": 3}, {"value": 50, "quantity": 2},
                                                   {"value": 100, "quantity": 1}]}}
        strict = True
