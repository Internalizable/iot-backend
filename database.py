# app/database.py

from decouple import config
from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine

MONGO_DETAILS = config('MONGO_DETAILS')
client = AsyncIOMotorClient(MONGO_DETAILS)
engine = AIOEngine(client, "iot")
