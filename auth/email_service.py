from fastapi import HTTPException
import requests
from config import BREVO_API_KEY

async def send_verification_email(email: str, otp: str):
    html_content = f"""<!DOCTYPE html>
<html>
  <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 2rem;">
    <div style="max-width: 500px; margin: auto; background-color: #000000; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); padding: 2rem; text-align: center;">

      <!-- Custom Logo -->
      <div style="width: 150px; height: 150px; position: relative; display: flex; justify-content: center; align-items: center; margin: 0 auto 1rem auto;">
        <div style="width: 100%; height: 100%; background-color: #3f45ff; border-radius: 50%; position: relative; overflow: hidden;">
          <div style="position: absolute; border: 5px solid white; border-radius: 75%; clip-path: inset(0 0 0 50% round 50%); width: 40%; height: 40%; top: 28%; left: 25%;"></div>
          <div style="position: absolute; border: 5px solid white; border-radius: 75%; clip-path: inset(0 0 0 50% round 50%); width: 60%; height: 60%; top: 18%; left: 15%;"></div>
          <div style="position: absolute; border: 5px solid white; border-radius: 75%; clip-path: inset(0 0 0 50% round 50%); width: 80%; height: 80%; top: 8%; left: 5%;"></div>
        </div>
      </div>

      <h2 style="color: #6366F1;">Welcome to Echo</h2>
      <p style="font-size: 1rem; color: #ffffff;">Use the following OTP to verify your email address:</p>
      <div style="font-size: 2rem; font-weight: bold; margin: 1rem 0; color: #FCD34D;">{otp}</div>
      <p style="color: #cccccc;">This OTP will expire in <strong>5 minutes</strong>.</p>
      <hr style="margin: 2rem 0; border: none; border-top: 1px solid #444;">
      <p style="font-size: 0.875rem; color: #888;">If you didn't request this, you can safely ignore this email.</p>
    </div>
  </body>
</html>
"""

    payload = {
        "sender": {"name": "Echo", "email": "no-reply@dev.sudheeshshetty.com"},
        "to": [{"email": email}],
        "subject": f"Your OTP: Code to sign in to Echo is {otp}",
        "htmlContent": html_content,
    }

    headers = {
        "api-key": BREVO_API_KEY,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post("https://api.brevo.com/v3/smtp/email", json=payload, headers=headers)
        response.raise_for_status()
        return {"message": "Email sent successfully", "response": response.json()}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Email sending failed: {e}")
