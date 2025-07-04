from datetime import timedelta
from jose import jwt
from fastapi import APIRouter, HTTPException, status
from config import REFRESH_SECRET
from .models import EmailRequest, OTPVerifyRequest, TokenRequest
from .utils import generate_otp, create_jwt, check_rate_limit, refresh_jwt, generate_random_username
from .email_service import send_verification_email
from database import redis_client, db

router = APIRouter(prefix="/auth")

@router.get("/")
async def root():
    return {"message": "Auth service is running"}

@router.post("/send-otp")
async def login(data: EmailRequest):
    await check_rate_limit(f"rate:login:{data.email}")
    otp = generate_otp()
    await redis_client.setex(f"otp:{data.email}", 300, otp)
    await send_verification_email(data.email, otp)
    return {"message": "OTP sent"}

@router.post("/verify")
async def verify(data: OTPVerifyRequest):
    await check_rate_limit(f"rate:verify:{data.email}")
    stored_otp = await redis_client.get(f"otp:{data.email}")
    if stored_otp != data.otp:
        raise HTTPException(status_code=401, detail="Invalid OTP")

    existing = await db.users.find_one({"email": data.email})
    if not existing:
        await db.users.insert_one({"email": data.email})

    access_token = create_jwt(data.email)
    refresh_token = refresh_jwt(data.email)
    await redis_client.setex(f"refresh:{data.email}", timedelta(days=30), refresh_token)
    return {"access_token": access_token,"refresh_token": refresh_token,"message": "OTP verified"}

@router.post("/refresh")
async def refresh(data: TokenRequest):
    refresh_token = data.refresh_token
    try:
        payload = jwt.decode(refresh_token, REFRESH_SECRET, algorithms=["HS256"])
        email = payload["sub"]
        stored_refresh_token = await redis_client.get(f"refresh:{email}")
        if not stored_refresh_token or stored_refresh_token.decode() != refresh_token:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        new_access_token = create_jwt(email)
        new_refresh_token = refresh_jwt(email)
        await redis_client.setex(f"refresh:{email}", timedelta(days=30), new_refresh_token)
        return {"access_token": new_access_token, "refresh_token": new_refresh_token}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code = 401, detail="Refresh token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code = 401, detail="Invalid refresh token")
    
@router.get('/random_username')
async def get_random_username():
    try:
        username = await generate_random_username()
        return {"username": username}
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to generate username")

