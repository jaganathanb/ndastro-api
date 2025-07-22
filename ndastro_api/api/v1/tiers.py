"""API endpoints for managing Tier resources (create, read, update, delete).

Includes endpoints for creating, listing, retrieving, updating, and deleting tiers.
"""

from typing import Annotated, cast

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ndastro_api.api.deps import get_current_superuser, get_current_user
from ndastro_api.api.v1.users import crud_tiers
from ndastro_api.core.db.database import async_get_db
from ndastro_api.core.exceptions.http_exceptions import (
    DuplicateValueException,
    NotFoundException,
)
from ndastro_api.schemas.pagination import PaginatedListResponse
from ndastro_api.schemas.tier import (  # Adjust the import path as needed
    TierCreate,
    TierCreateInternal,
    TierRead,
    TierUpdate,
)
from ndastro_api.services.utils import compute_offset, paginated_response

router = APIRouter(tags=["Tiers"], prefix="/tiers")


@router.post("/", dependencies=[Depends(get_current_superuser)], status_code=201, summary="Create a new tier.")
async def write_tier(
    tier: TierCreate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> TierRead:
    """Create a new tier. Only superusers can create tiers.

    Raises DuplicateValueException if a tier with the same name exists.
    Returns the created TierRead object.
    """
    tier_internal_dict = tier.model_dump()
    db_tier = await crud_tiers.exists(db=db, name=tier_internal_dict["name"])
    if db_tier:
        msg = "Tier Name"
        raise DuplicateValueException(msg)

    tier_internal = TierCreateInternal(**tier_internal_dict)
    created_tier = await crud_tiers.create(db=db, object=tier_internal)

    tier_read = await crud_tiers.get(db=db, id=created_tier.id, schema_to_select=TierRead)
    if tier_read is None:
        raise NotFoundException

    return cast("TierRead", tier_read)


@router.get(
    "/", dependencies=[Depends(get_current_user)], response_model=PaginatedListResponse[TierRead], summary="Get a paginated list of all tiers."
)
async def read_tiers(
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int = 1,
    items_per_page: int = 10,
) -> dict:
    """Get a paginated list of all tiers."""
    tiers_data = await crud_tiers.get_multi(db=db, offset=compute_offset(page, items_per_page), limit=items_per_page)

    response: dict[str, TierRead] = paginated_response(crud_data=tiers_data, page=page, items_per_page=items_per_page)
    return response


@router.get("/{name}", dependencies=[Depends(get_current_user)], summary="Get a tier by name.")
async def read_tier(
    name: str,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> TierRead:
    """Get a tier by name. Raises NotFoundException if not found."""
    db_tier = await crud_tiers.get(db=db, name=name, schema_to_select=TierRead)
    if db_tier is None:
        raise NotFoundException

    return cast("TierRead", db_tier)


@router.patch("/{name}", dependencies=[Depends(get_current_superuser)], summary="Update a tier by name.")
async def patch_tier(
    name: str,
    values: TierUpdate,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, str]:
    """Update a tier by name. Only superusers can update. Raises NotFoundException if not found."""
    db_tier = await crud_tiers.get(db=db, name=name, schema_to_select=TierRead)
    if db_tier is None:
        raise NotFoundException

    await crud_tiers.update(db=db, object=values, name=name)
    return {"message": "Tier updated"}


@router.delete("/{name}", dependencies=[Depends(get_current_superuser)], summary="Delete a tier by name.")
async def erase_tier(
    name: str,
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, str]:
    """Delete a tier by name. Only superusers can delete. Raises NotFoundException if not found."""
    db_tier = await crud_tiers.get(db=db, name=name, schema_to_select=TierRead)
    if db_tier is None:
        raise NotFoundException

    await crud_tiers.delete(db=db, name=name)
    return {"message": "Tier deleted"}
