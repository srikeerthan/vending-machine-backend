from typing import List

from pydantic import BaseModel, Field


class PurchaseInUpdate(BaseModel):
    ...


class PurchaseItem(BaseModel):
    product_id: int = Field(strict=True, gt=0)
    quantity: int = Field(strict=True, gt=0)


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
    value: int = Field(strict=True, gt=0)
    quantity: int = Field(strict=True, gt=0)


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
