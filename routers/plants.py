# app/routers/plants.py
import uuid

from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect

from main import get_socket_manager
from utils.auth import get_current_user
from database import iot
from inputs.plant_input import PlantInput
from utils.json_encoder import jsonable_encoder
from models.plant import Plant
from models.user import User
from utils.websocket_manager import WebSocketManager

router = APIRouter()


@router.post("/plants/create")
async def create_plant(plant_input: PlantInput, current_user: User = Depends(get_current_user)):
    plant = Plant(
        name=plant_input.name,
        description=plant_input.description,
        key=str(uuid.uuid4()),
        temperatures=[],
        humidities=[],
        moistures=[],
        light_values=[]
    )

    new_plant_dict = plant.to_mongo().to_dict()

    try:
        new_sensor = await iot['plants'].insert_one(new_plant_dict)
        created_sensor = await iot['plants'].find_one({"_id": new_sensor.inserted_id})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

    return jsonable_encoder(created_sensor)


@router.websocket("/plants/listen/{plant_id}")
async def listen_plant(websocket: WebSocket, plant_id: str, current_user: User = Depends(get_current_user),
                       manager: WebSocketManager = Depends(get_socket_manager)):
    # todo check if plant_id exists then connect.
    await manager.connect(websocket, plant_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, plant_id)
