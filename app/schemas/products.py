from typing import Optional

from pydantic import BaseModel, Field, ConfigDict, condecimal


class Product(BaseModel):
    name: str
    price: condecimal(max_digits=11, decimal_places=2)
    quantity: int


class ProductInCreate(Product):
    name: str = Field(..., title="Product Name")
    price: condecimal(max_digits=11, decimal_places=2) = Field(..., title="Product Price")
    quantity: int = Field(..., title="Product Quantity")


class ProductInUpdate(Product):
    name: Optional[str] = Field(..., title="Product Name")
    price: Optional[condecimal(max_digits=11, decimal_places=2)] = Field(..., title="Product Price")
    quantity: Optional[int] = Field(..., title="Product Quantity")


class ProductInDB(Product):
    model_config = ConfigDict(from_attributes=True)
