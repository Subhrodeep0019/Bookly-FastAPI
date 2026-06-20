import redis.asyncio as redis
from src.config import setting

jti_expiry=600 # 5 min

token_blocklist = redis.Redis(
    host=setting.REDIS_HOST,
    port=setting.REDIS_PORT
)

async def add_to_blocklist(jti: str) -> None:
    await token_blocklist.set(name=jti, value="", ex=jti_expiry)

async def is_in_blocklist(jti: str) -> bool:
    jti = await token_blocklist.get(jti)
    # return jti != None
    return jti is not None