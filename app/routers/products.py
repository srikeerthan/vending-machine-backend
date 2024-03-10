from typing import List

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user, get_current_product
from app.core.pagination import Pagination, pagination_params
from app.models.products import Products
from app.models.users import Users
from app.schemas.products import ProductResponse, ProductInCreate, ProductInUpdate, ProductDeleteResponse, \
    ProductsPaginationResponse
from app.schemas.response import Response
from app.services.products import ProductsService

router = APIRouter()


@router.post("", response_model=Response[ProductResponse])
async def create_product(product: ProductInCreate, current_user: Users = Depends(get_current_user),
                         products_service: ProductsService = Depends()) -> Response:
    product = products_service.create_product(product, current_user)
    return Response(data=product, message="Product created successfully")


@router.get("", response_model=Response[ProductsPaginationResponse])
async def get_all_products(pagination: Pagination = Depends(pagination_params),
                           products_service: ProductsService = Depends()) -> Response:
    products = products_service.get_all_products(pagination)
    return Response(data=products, message="Products fetched successfully")


@router.get("/{product_id}", response_model=Response[ProductResponse])
async def get_product(product_id: int, products_service: ProductsService = Depends()):
    product = products_service.get_product_by_id(product_id)
    return Response(data=product, message="Product fetched successfully")


@router.put("/{product_id}", response_model=Response[ProductResponse])
async def update_product(product_in_update: ProductInUpdate, current_product: Products = Depends(get_current_product),
                         products_service: ProductsService = Depends()) -> Response:
    product = products_service.update_product(product_in_update, current_product)
    return Response(data=product, message="Product updated successfully")


@router.delete("/{product_id}", response_model=Response[ProductDeleteResponse])
async def delete_product(product: Products = Depends(get_current_product),
                         products_service: ProductsService = Depends()) -> Response:
    product = products_service.delete_product(product)
    return Response(data=product, message=f"Product: {product.name} deleted successfully")
