from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user, get_current_deposit
from app.models.deposits import Deposits
from app.models.users import Users
from app.schemas.deposits import DepositsResponse, DepositInCreate, DepositResetResponse
from app.schemas.response import Response
from app.services.deposits import DepositsService

router = APIRouter()


@router.post("", response_model=Response[DepositsResponse])
async def create_deposit(deposit: DepositInCreate, current_user: Users = Depends(get_current_user),
                         deposits_service: DepositsService = Depends()) -> Response:
    deposit = deposits_service.create_deposit(deposit, current_user)
    return Response(data=deposit, message="Deposit successful")


@router.post("/reset", response_model=Response[DepositResetResponse])
async def reset_deposits(current_deposit: Deposits = Depends(get_current_deposit),
                         deposits_service: DepositsService = Depends()) -> Response:
    deposit = deposits_service.reset_deposit(current_deposit)
    return Response(data=deposit, message="Deposit reset successful")
