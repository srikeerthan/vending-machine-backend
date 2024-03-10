from enum import Enum

from fastapi import Query
from pydantic import BaseModel


class SortEnum(Enum):
    ASCENDING = "asc"
    DESCENDING = "desc"


class Pagination(BaseModel):
    page: int
    per_page: int
    order: SortEnum


def pagination_params(page: int = Query(default=1, ge=1, required=False),
                      per_page: int = Query(default=100, ge=1, le=100, required=False),
                      order: SortEnum = SortEnum.DESCENDING) -> Pagination:
    return Pagination(page=page, per_page=per_page, order=order)
