from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_current_product
from app.models.products import Products
from app.models.users import Users
from app.schemas.products import ProductInDB, ProductInCreate, ProductInUpdate
from app.schemas.response import Response
from app.services.products import ProductsService

router = APIRouter()


@router.post("", response_model=Response[ProductInDB])
async def create_product(product: ProductInCreate, current_user: Users = Depends(get_current_user),
                         products_service: ProductsService = Depends()) -> Response:
    product = products_service.create_product(product, current_user)
    return Response(data=product, message="Product created successfully")


@router.get("", response_model=Response[List[ProductInDB]])
async def get_all_products(products_service: ProductsService = Depends()) -> Response:
    products = products_service.get_all_products()
    return Response(data=products, message="Products fetched successfully")


@router.put("/{product_id}", response_model=Response[ProductInDB])
async def update_product(product_in_update: ProductInUpdate, current_product: Products = Depends(get_current_product),
                         products_service: ProductsService = Depends()) -> Response:
    product = products_service.update_product(product_in_update, current_product)
    return Response(data=product, message=f"Product with id {product.id} updated successfully")


@router.delete("/{product_id}", response_model=Response[ProductInDB])
async def delete_product(product: Products = Depends(get_current_product),
                         products_service: ProductsService = Depends()) -> Response:
    product = products_service.delete_product(product)
    return Response(data=product, message=f"Product with id {product.id} deleted successfully")
