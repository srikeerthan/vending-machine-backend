from http import HTTPStatus
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import (
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
)


def form_error_message(errors: List[dict]) -> List[str]:
    """
    Make valid pydantic `ValidationError` messages list.
    """
    messages = []
    for error in errors:
        field, message = error["loc"][-1], error["msg"]
        messages.append(f"`{field}` {message}")
    return messages


class BaseInternalException(Exception):
    """
    Base error class for inherit all internal errors.
    """

    def __init__(self, message: str, status_code: int) -> None:
        self.message = message
        self.status_code = status_code


class UserAlreadyExistException(BaseInternalException):
    """
    Exception raised when existing username is used while user creation.
    """


class InvalidRolesException(BaseInternalException):
    """
    Exception raised when invalid roles are passed for the users
    """


class UserNotFoundException(BaseInternalException):
    """
    Exception raised when user try to register with already exist username.
    """


class InvalidUserCredentialsException(BaseInternalException):
    """
    Exception raised when user try to login with invalid credentials.
    """


class InvalidInputDataException(BaseInternalException):
    """
    Exception raised when invalid data is passed as input
    """


class InactiveUserAccountException(BaseInternalException):
    """
    Exception raised when user try to login to inactive account.
    """


class UserPermissionException(BaseInternalException):
    """
    Exception raised when user try to read product from other owner.
    """


class ProductNotFoundException(BaseInternalException):
    """
    Exception raised when product is not found
    """


class ProductAlreadyExistsException(BaseInternalException):
    """
    Exception raised when product already exists with same name
    """


class DepositsAlreadyExistsException(BaseInternalException):
    """
    Exception raised when not utilized deposits already exists for user
    """


class DepositsNotExistsException(BaseInternalException):
    """
    Exception raised when not utilized deposits does not exists for uer
    """


def add_internal_exception_handler(app: FastAPI) -> None:
    """
    Handle all internal exceptions.
    """

    @app.exception_handler(BaseInternalException)
    async def _exception_handler(
            _: Request, exc: BaseInternalException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "status": exc.status_code,
                "type": type(exc).__name__,
                "message": exc.message,
            },
        )


def add_validation_exception_handler(app: FastAPI) -> None:
    """
    Handle `pydantic` validation errors exceptions.
    """

    @app.exception_handler(ValidationError)
    async def _exception_handler(_: Request, exc: ValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "status": HTTPStatus.UNPROCESSABLE_ENTITY,
                "type": "ValidationError",
                "message": "Schema validation error",
                "errors": form_error_message(errors=exc.errors()),
            },
        )


def add_request_exception_handler(app: FastAPI) -> None:
    """
    Handle request validation errors exceptions.
    """

    @app.exception_handler(RequestValidationError)
    async def _exception_handler(
            _: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "status": HTTPStatus.UNPROCESSABLE_ENTITY,
                "type": "RequestValidationError",
                "message": "Schema validation error",
                "errors": form_error_message(errors=exc.errors()),
            },
        )


def add_http_exception_handler(app: FastAPI) -> None:
    """
    Handle http exceptions.
    """

    @app.exception_handler(HTTPException)
    async def _exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "status": exc.status_code,
                "type": "HTTPException",
                "message": exc.detail,
            },
        )


def add_internal_server_error_handler(app: FastAPI) -> None:
    """
    Handle http exceptions.
    """

    @app.exception_handler(Exception)
    async def _exception_handler(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "status": HTTPStatus.INTERNAL_SERVER_ERROR,
                "type": "HTTPException",
                "message": "Internal Server Error",
            },
        )


def add_exceptions_handlers(app: FastAPI) -> None:
    """
    Base exception handlers.
    """
    add_internal_exception_handler(app=app)
    add_validation_exception_handler(app=app)
    add_request_exception_handler(app=app)
    add_http_exception_handler(app=app)
    add_internal_server_error_handler(app=app)
