import datetime
import random, string
from jose import jwt
from config import JWT_SECRET, REFRESH_SECRET
from fastapi import HTTPException
from database import redis_client

def generate_otp(length=5):
    """
    Generates a random numeric OTP of a given length.

    Args:
        length: The length of the OTP to generate, defaults to 5.

    Returns:
        A string of length `length` consisting of random digits.
    """
    return ''.join(random.choices(string.digits, k=length))

def create_jwt(email: str):
    """
    Creates a JWT token for the given email address.

    Args:
        email: The email address for which to create the token.

    Returns:
        A string containing the JWT token.

    Notes:
        The token will expire in 7 days.
    """
    return jwt.encode({
        "sub": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }, JWT_SECRET, algorithm="HS256")

def refresh_jwt(email: str):
    """
    Creates a refresh JWT token for the given email address.

    Args:
        email: The email address for which to create the refresh token.

    Returns:
        A string containing the refresh JWT token.

    Notes:
        The refresh token will expire in 30 days.
    """

    return jwt.encode({
        "sub": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=30)
    }, REFRESH_SECRET, algorithm="HS256")

async def check_rate_limit(key: str, limit: int = 5, window: int = 300):
    """
    Checks a rate limit for the given key.

    Args:
        key: The Redis key to use for the rate limit.
        limit: The number of requests allowed within the given window.
        window: The time in seconds for the rate limit.

    Raises:
        HTTPException: If the rate limit has been exceeded.
    """
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
