from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI
from redis.asyncio import Redis

client = AsyncIOMotorClient(MONGO_URI)
db = client["echo"]

redis_client = Redis.from_url("redis://localhost", decode_responses=True)
