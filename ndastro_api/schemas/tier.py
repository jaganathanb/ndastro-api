"""Schemas for tier-related data models in the ndastro API.

This module defines Pydantic models for tier creation, reading, updating, and deletion.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Annotated

from pydantic import BaseModel, Field

from ndastro_api.core.schemas import TimestampSchema

if TYPE_CHECKING:
    from datetime import datetime


class TierBase(BaseModel):
    """Base schema for tier information (e.g., name of the tier)."""

    name: Annotated[str, Field(examples=["free"])]


class TierSchema(TimestampSchema, TierBase):
    """Full tier schema including timestamp fields."""

    id: str | None = None


class TierRead(TierBase):
    """Schema for reading tier information, including id and creation time."""

    id: int
    created_at: datetime


TierRead.model_rebuild()


class TierCreate(TierBase):
    """Schema for creating a new tier."""


class TierCreateInternal(TierCreate):
    """Internal schema for creating a tier (can be extended for internal use)."""


class TierUpdate(BaseModel):
    """Schema for updating tier information (name is optional)."""

    name: str | None = None


class TierUpdateInternal(TierUpdate):
    """Schema for internal tier update, including updated_at timestamp."""

    updated_at: datetime


class TierDelete(BaseModel):
    """Schema for deleting a tier (can be extended for soft/hard delete)."""
