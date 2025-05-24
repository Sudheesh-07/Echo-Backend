import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
JWT_SECRET = os.getenv("JWT_SECRET")
BREVO_API_KEY = os.getenv("BREVO_API_KEY")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
