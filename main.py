import asyncio

from fastapi import FastAPI, Depends

from routers import plants, users
from utils.mqtt_manager import MQTTManager
from dependencies.dependencies import get_socket_manager

app = FastAPI()

app.include_router(plants.router, dependencies=[Depends(get_socket_manager)])
app.include_router(users.router)


@app.on_event("startup")
async def startup_event():
    client = MQTTManager(get_socket_manager())
    asyncio.create_task(client.connect("test.mosquitto.org"))


@app.get("/")
async def root():
    return {"message": "Welcome to the IOT API! 🚀"}
