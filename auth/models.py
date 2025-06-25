from pydantic import BaseModel, EmailStr

class EmailRequest(BaseModel):
    email: EmailStr

class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp: str

class TokenRequest(BaseModel):
    refresh_token: str