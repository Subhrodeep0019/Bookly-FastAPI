from typing import List
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer
from sqlmodel.ext.asyncio.session import AsyncSession
from .utils import decode_token
from src.db.redis_client import is_in_blocklist
from src.db.main import get_session
from src.db.model import User
from .service import UserService
from src.errors import (
    InvalidToken,
    RevokedToken,
    AccessTokenRequired,
    RefreshTokenRequired,
    InsufficientPermission,
    UserNotFound
)


user_service = UserService()

class TokenBearer(HTTPBearer):
    def __init__(self, auto_error = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        creds = await super().__call__(request)
        token = creds.credentials

        payload = decode_token(token)
        if not payload:
            raise InvalidToken()

        await self.token_in_blocklist(payload)
        self.verify_token_data(payload)
        return payload

    def verify_token_data(self, payload: dict ):
        raise NotImplementedError("Override in Subclass")

    async def token_in_blocklist(self, payload: dict):
        jti = payload.get("jti")
        # If the "jti" key is missing, or this token's jti is in the blocklist, reject it.
        if not jti or await is_in_blocklist(jti):
            raise RevokedToken()

class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, payload: dict ):
        if payload.get("refresh", False):
            raise AccessTokenRequired()

class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, payload: dict ):
        if not payload.get("refresh", False):
            raise RefreshTokenRequired()

async def get_curr_user(
        payload: dict = Depends(AccessTokenBearer()),
        session: AsyncSession = Depends(get_session)
) -> User:
    u_email = payload.get("user", {}).get("email")
    curr_user = await user_service.get_user_by_email(u_email, session)
    if not curr_user:
        raise UserNotFound()
    return curr_user

class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user_det: User = Depends(get_curr_user)):
        if user_det.role in self.allowed_roles:
            return True
        raise InsufficientPermission()