import random, string
from jose import jwt
from config import JWT_SECRET
from fastapi import HTTPException
from database import redis_client

def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))

def create_jwt(email: str):
    return jwt.encode({"sub": email}, JWT_SECRET, algorithm="HS256")

async def check_rate_limit(key: str, limit: int = 5, window: int = 300):
    count = await redis_client.get(key)
    if count is not None and int(count) >= limit:
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please try again later."
        )

    txn = redis_client.pipeline()
    txn.incr(key)
    txn.expire(key, window)
    await txn.execute()
