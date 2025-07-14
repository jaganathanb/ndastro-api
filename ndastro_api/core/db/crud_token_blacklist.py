"""CRUD operations for the TokenBlacklist table using FastCRUD."""

from fastcrud import FastCRUD

from ndastro_api.core.db.token_blacklist import TokenBlacklist
from ndastro_api.core.schemas import (
    TokenBlacklistCreate,
    TokenBlacklistRead,
    TokenBlacklistUpdate,
)

CRUDTokenBlacklist = FastCRUD[
    TokenBlacklist,
    TokenBlacklistCreate,
    TokenBlacklistUpdate,
    TokenBlacklistUpdate,
    TokenBlacklistUpdate,
    TokenBlacklistRead,
]
crud_token_blacklist = CRUDTokenBlacklist(TokenBlacklist)
