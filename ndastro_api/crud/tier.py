"""CRUD operations for Tier entities using FastCRUD.

This module defines the CRUDTier class and an instance for managing Tier-related database operations.
"""

from fastcrud import FastCRUD

from ndastro_api.models.tier import Tier
from ndastro_api.schemas.tier import (
    TierCreateInternal,
    TierDelete,
    TierRead,
    TierUpdate,
    TierUpdateInternal,
)

CRUDTier = FastCRUD[Tier, TierCreateInternal, TierUpdate, TierUpdateInternal, TierDelete, TierRead]
crud_tiers = CRUDTier(Tier)
