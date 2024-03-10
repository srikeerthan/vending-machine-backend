from typing import Optional, List

from fastapi import status
from pydantic import BaseModel, Field, field_validator, root_validator, model_validator

from app.core.exceptions import InvalidInputDataException


class Product(BaseModel):
    name: str = Field(title="Product Name", strict=True, min_length=1, max_length=100)
    price: float = Field(title="Product Price", strict=True, ge=0.01)
    quantity: int = Field(title="Product Quantity", strict=True, gt=0)

    @field_validator('price')
    def validate_price(cls, v):
        if round(v, 2) != v:
            raise InvalidInputDataException(message="Price must have less than or equal to two decimal places",
                                            status_code=status.HTTP_400_BAD_REQUEST)
        return v


class ProductInCreate(Product):
    ...


class ProductInUpdate(Product):
    name: Optional[str] = Field(None, title="Product Name", strict=True, min_length=1, max_length=100)
    price: Optional[float] = Field(None, title="Product Price", strict=True, ge=0.01)
    quantity: Optional[int] = Field(None, title="Product Quantity", strict=True, gt=0)

    @field_validator('price', mode='after')
    def validate_price(cls, v):
        if round(v, 2) != v:
            raise InvalidInputDataException(message="Price must have less than or equal to two decimal places",
                                            status_code=status.HTTP_400_BAD_REQUEST)
        return v

    @model_validator(mode="after")
    def check_at_least_one_field_present(self) -> 'ProductInUpdate':
        if not (self.name or self.price or self.quantity):
            raise InvalidInputDataException(
                message="At least one field (name, price, quantity) must be specified for update",
                status_code=status.HTTP_400_BAD_REQUEST)
        return self


class ProductResponse(Product):
    id: int = Field(title="Product ID")
    name: str = Field(title="Product Name")
    price: float = Field(title="Product Price")
    quantity: int = Field(title="Product Quantity")

    class Config:
        json_schema_extra = {
            "example": {"id": 22, "name": "lays", "price": 1.5, "quantity": 5}}


class ProductItem(BaseModel):
    id: int = Field(title="Product ID")
    name: str = Field(title="Product Name")
    price: float = Field(title="Product Price")
    quantity: int = Field(title="Product Quantity")


class ProductsPaginationResponse(BaseModel):
    count: int
    products: List[ProductItem]

    class Config:
        json_schema_extra = {
            "example": {"count": 5, "products": [{"id": 22, "name": "lays", "price": 1.5, "quantity": 5},
                                                 {"id": 23, "name": "bingo", "price": 1.5, "quantity": 5}]}}


class ProductDeleteResponse(BaseModel):
    ...
