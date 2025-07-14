"""Pydantic v2-compatible generic paginated response schema."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedListResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper for list endpoints."""

    items: list[T]
    total: int
    page: int
    items_per_page: int
    next_page: int | None = None
    prev_page: int | None = None
