import logging
from typing import Any, Dict, List, Optional, Type

from sqlalchemy import Pool

from version import response

from app.core.settings.base import BaseAppSettings
from pydantic import ConfigDict


class AppSettings(BaseAppSettings):
    """
    Base application settings
    """

    debug: bool = False
    docs_url: str = "/"
    openapi_prefix: str = ""
    openapi_url: str = "/openapi.json"
    redoc_url: str = "/redoc"
    title: str = response["message"]
    version: str = response["version"]

    secret_key: str

    api_prefix: str = "/api/v1"

    allowed_hosts: List[str] = ["*"]

    logging_level: int = logging.INFO

    database_url: str
    postgres_port: str
    postgres_db: str
    postgres_user: str
    postgres_password: str
    min_connection_count: int = 5
    max_connection_count: int = 10
    model_config = ConfigDict(validate_assignment=True)

    @property
    def fastapi_kwargs(self) -> Dict[str, Any]:
        return {
            "debug": self.debug,
            "docs_url": self.docs_url,
            "openapi_prefix": self.openapi_prefix,
            "openapi_url": self.openapi_url,
            "redoc_url": self.redoc_url,
            "title": self.title,
            "version": self.version,
        }
