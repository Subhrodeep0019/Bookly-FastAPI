from uuid import uuid4
from pwdlib import PasswordHash
from datetime import timedelta, datetime, timezone
import jwt
from src.config import setting
import logging


access_token_expiry = 3600 # 1 hour
pass_hash = PasswordHash.recommended()

def generate_hash(pwd: str) -> str:
    return pass_hash.hash(pwd)

def verify_pass(pwd: str, hashed: str) -> bool:
    return pass_hash.verify(pwd, hashed)

def create_token(user_data: dict, expiry: timedelta|None = None, refresh: bool = False) -> str:
    if expiry is None:
        expiry = timedelta(seconds=access_token_expiry)

    payload = {
        "user": user_data,
        "exp": datetime.now(timezone.utc) + expiry,
        # same payload info(w/o uuid) can generate same jwt token
        # so using uuid to generate absolutely unique jwt token
        # at every login from same user
        "jti": str(uuid4()),
        "refresh": refresh
    }

    my_token = jwt.encode(
        payload=payload,
        key=setting.JWT_SECRET,
        algorithm=setting.JWT_ALGORITHM
    )

    return my_token

def decode_token(token: str) -> dict|None:
    try:
        token_data = jwt.decode(
            jwt=token,
            key=setting.JWT_SECRET,
            algorithms=[setting.JWT_ALGORITHM]
        )
        return token_data # payload
    except jwt.PyJWTError as e:
        logging.exception(e)
        return None

