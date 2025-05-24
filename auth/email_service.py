import requests
from config import BREVO_API_KEY

async def send_verification_email(email: str, otp: str):
    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 2rem;">
        <div style="max-width: 500px; margin: auto; background-color: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); padding: 2rem; text-align: center;">
          <h2 style="color: #6366F1;">Welcome to Echo</h2>
          <p style="font-size: 1rem; color: #333;">Use the following OTP to verify your email address:</p>
          <div style="font-size: 2rem; font-weight: bold; margin: 1rem 0; color: #FCD34D;">{otp}</div>
          <p style="color: #666;">This OTP will expire in <strong>5 minutes</strong>.</p>
          <hr style="margin: 2rem 0;">
          <p style="font-size: 0.875rem; color: #aaa;">If you didn't request this, you can safely ignore this email.</p>
        </div>
      </body>
    </html>
    """

    payload = {
        "sender": {"name": "Echo", "email": "no-reply@dev.sudheeshshetty.com"},
        "to": [{"email": email}],
        "subject": "Your OTP Code - Echo",
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
        raise HTTPException(status_code=400, detail=str(e))
