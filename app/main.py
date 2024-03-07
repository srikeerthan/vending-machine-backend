from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_app_settings
from app.core.exceptions import add_exceptions_handlers
from app.routers.base_router import router as api_router


def create_app() -> FastAPI:
    """
    Application factory, used to create application.
    """
    settings = get_app_settings()

    application = FastAPI(**settings.fastapi_kwargs)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_hosts,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(api_router, prefix="/api/v1")

    add_exceptions_handlers(app=application)

    return application


app = create_app()

# @app.get("/")
# async def root():
#     return {"message": "Hello World"}
#
#
# @app.get("/hello/{name}")
# async def say_hello(name: str):
#     return {"message": f"Hello {name}"}
