from idlelib.window import add_windows_to_menu

from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer
from sqlmodel.ext.asyncio.session import AsyncSession
from .utils import decode_token
from src.db.redis_client import is_in_blocklist
from src.db.main import get_session
from .model import User
from .service import UserService


user_service = UserService()

class TokenBearer(HTTPBearer):
    def __init__(self, auto_error = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        creds = await super().__call__(request)
        token = creds.credentials

        payload = decode_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "invalid or expired token",
                    "resolution": "please get a new access token"
                }
            )
        await self.token_in_blocklist(payload)
        self.verify_token_data(payload)
        return payload


    def verify_token_data(self, payload: dict ):
        raise NotImplementedError("Override in Subclass")


    async def token_in_blocklist(self, payload: dict):
        jti = payload.get("jti")
        # If the "jti" key is missing, or this token's jti is in the blocklist, reject it.
        if not jti or await is_in_blocklist(jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "invalid or revoked token",
                    "resolution": "please get a new access token"
                }
            )



class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, payload: dict ):
        if payload.get("refresh", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Refresh Token Not Allowed"
            )


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, payload: dict ):
        if not payload.get("refresh", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Refresh Token Allowed"
            )



async def get_curr_user(
        payload: dict = Depends(AccessTokenBearer()),
        session: AsyncSession = Depends(get_session)
) -> User | None:
    u_email = payload.get("user", {}).get("email")
    curr_user = await user_service.get_user_by_email(u_email, session)
    return curr_user



