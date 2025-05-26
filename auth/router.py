from fastapi import APIRouter, HTTPException, status
from .models import EmailRequest, OTPVerifyRequest
from .utils import generate_otp, create_jwt, check_rate_limit
from .email_service import send_verification_email
from database import redis_client, db

router = APIRouter(prefix="/auth")
home = APIRouter()
@home.get("/")
async def home():
    return {"message": "Hello World"}

@router.post("/login")
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

    token = create_jwt(data.email)
    return {"token": token}

