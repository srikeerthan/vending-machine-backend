from fastapi import APIRouter

from app.routers import users, products, deposits, purchases

router = APIRouter()

router.include_router(router=users.router, tags=["Users"], prefix="/users")
router.include_router(router=products.router, tags=["Products"], prefix="/products")
router.include_router(router=deposits.router, tags=["Deposits"], prefix="/deposits")
router.include_router(router=purchases.router, tags=["Purchases"], prefix="/buy")
