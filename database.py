# app/database.py

from motor.motor_asyncio import AsyncIOMotorClient
from decouple import config

MONGO_DETAILS = config('MONGO_DETAILS')

client = AsyncIOMotorClient(MONGO_DETAILS)

iot = client.iot
