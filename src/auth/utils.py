from uuid import uuid4
from pwdlib import PasswordHash
from datetime import timedelta, datetime, timezone
from src.config import setting
import jwt
import logging
from itsdangerous import URLSafeTimedSerializer


access_token_expiry = 600 # 10 min
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


serializer = URLSafeTimedSerializer(
    secret_key=setting.JWT_SECRET,
    salt="email-verification"
)

def create_url_safe_token(data: dict) -> str:
    token = serializer.dumps(data)
    return token

def decode_url_safe_token(token: str) -> dict | None:
    try:
        token_data = serializer.loads(token, max_age=3600)
        return token_data
    except Exception as e:
        logging.error(str(e))

