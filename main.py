from fastapi import FastAPI, Depends

from routers import plants, users
from utils.mqtt_manager import MQTTManager
from utils.websocket_manager import WebSocketManager

app = FastAPI()

socketManager = WebSocketManager()
mqtt_manager = MQTTManager(socketManager)
mqtt_manager.connect("test.mosquitto.org")


def get_socket_manager():
    return socketManager


app.include_router(plants.router, dependencies=[Depends(get_socket_manager)])
app.include_router(users.router)


@app.get("/")
async def root():
    return {"message": "Welcome to the IOT API! 🚀"}
