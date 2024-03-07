from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_deposit
from app.models.deposits import Deposits
from app.schemas.purchases import PurchaseResponse, PurchaseInCreate
from app.schemas.response import Response
from app.services.purchases import PurchasesService

router = APIRouter()


@router.post("", response_model=Response[PurchaseResponse])
async def create_purchase(purchase: PurchaseInCreate,
                          current_deposit: Deposits = Depends(get_current_deposit),
                          purchase_service: PurchasesService = Depends()) -> Response:
    purchases = purchase_service.buy_products(purchase, current_deposit)
    return Response(data=purchases, message="Products purchase completed successfully")
