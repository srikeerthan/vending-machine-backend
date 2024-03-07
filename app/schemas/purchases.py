from typing import List

from fastapi import status
from pydantic import BaseModel, field_validator

from app.core.exceptions import InvalidInputDataException


class PurchaseInUpdate(BaseModel):
    ...


class PurchaseItem(BaseModel):
    product_id: int
    quantity: int

    @field_validator('quantity')
    def check_negative_quantity(cls, v):
        if v < 0:
            raise InvalidInputDataException(message="Product quantity cannot be negative",
                                            status_code=status.HTTP_400_BAD_REQUEST)
        return v


class PurchaseInCreate(BaseModel):
    products: List[PurchaseItem]

    class Config:
        json_schema_extra = {
            "example": {
                "products": [
                    {
                        "product_id": 123,
                        "quantity": 2
                    },
                    {
                        "product_id": 456,
                        "quantity": 1
                    }
                ]
            }
        }


class CoinItem(BaseModel):
    value: int
    quantity: int


class PurchaseResponse(BaseModel):
    total_spent: float
    products: List[PurchaseItem]
    change: List[CoinItem]

    class Config:
        json_schema_extra = {
            "example": {
                "total_spent": 4.5,
                "products": [
                    {
                        "product_id": 123,
                        "quantity": 2
                    },
                    {
                        "product_id": 134,
                        "quantity": 3
                    }
                ],
                "change": [
                    {
                        "value": 5,
                        "quantity": 2
                    },
                    {
                        "value": 10,
                        "quantity": 3
                    }
                ]  # Change in cents (e.g., 10 cents and 5 cents)
            }
        }
