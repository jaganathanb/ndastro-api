"""API endpoints for user-specific settings management."""

from fastapi import APIRouter, Depends, HTTPException

from ndastro_api.api.deps import SessionDep, get_current_user
from ndastro_api.models import User, UserSetting
from ndastro_api.services.users import (
    get_user_setting,
    get_user_settings,
    set_user_setting,
)

router = APIRouter(prefix="/user-settings", tags=["user-settings"])


@router.get("/", response_model=list[UserSetting])
def read_user_settings(
    session: SessionDep,
    current_user: User = Depends(get_current_user),
) -> list[UserSetting]:
    """Get all settings for the current user."""
    return get_user_settings(session=session, user_id=current_user.id)


@router.get("/{section}/{key}", response_model=UserSetting)
def read_user_setting(
    section: str,
    key: str,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
) -> UserSetting:
    """Get a specific user setting by section and key."""
    setting = get_user_setting(session=session, user_id=current_user.id, section=section, key=key)
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return setting


@router.put("/{section}/{key}", response_model=UserSetting)
def update_user_setting(
    section: str,
    key: str,
    value: str,
    session: SessionDep,
    current_user: User = Depends(get_current_user),
) -> UserSetting:
    """Set or update a user setting (upsert)."""
    return set_user_setting(session=session, user_id=current_user.id, section=section, key=key, value=value)
