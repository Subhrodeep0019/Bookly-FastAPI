from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from .utils import decode_token


class AccessTokenBearer(HTTPBearer):
    def __init__(self, auto_err = True):
        super().__init__(auto_error=auto_err)

    async def __call__(self, request: Request):
        creds = await super().__call__(request)
        token = creds.credentials

        payload = decode_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Session Token"
            )
        if payload["refresh"]: # if this is a refresh token
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Refresh Token Not Allowed"
            )

        return payload




