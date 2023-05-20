import asyncio

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from database import engine
from models.plant import Plant
from models.user import User
from routers import plants, users
from utils.mqtt_manager import MQTTManager
from ai.aimodel import AIModel
from dependencies.dependencies import get_socket_manager

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080", "http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(plants.router, dependencies=[Depends(get_socket_manager)])
app.include_router(users.router)


@app.on_event("startup")
async def startup_event():
    model = AIModel()
    model.train("dataset.xlsx")

    client = MQTTManager(get_socket_manager(), model)
    asyncio.create_task(client.connect("test.mosquitto.org"))

    await engine.configure_database([User, Plant])


@app.get("/")
async def root():
    return {"message": "Welcome to the IOT API! 🚀"}
