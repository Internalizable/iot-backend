# app/routers/plants.py
import uuid

from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.params import Query

from database import engine
from dependencies.dependencies import get_socket_manager
from inputs.plant_input import PlantInput
from models.plant import Plant
from models.user import User
from utils.auth import get_current_user
from utils.json_encoder import jsonable_encoder
from utils.websocket_manager import WebSocketManager

router = APIRouter()


# Authorization: Bearer [token]

@router.get("/plants/")
async def get_all_plant(current_user: User = Depends(get_current_user)):
    try:
        pipeline = [
            {"$project": {"name": 1, "description": 1, "key": 1, "state": 1}}
        ]

        queried_sensors = await engine.aggregate(Plant, pipeline=pipeline)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

    return jsonable_encoder(queried_sensors)


@router.get("/plants/{plant_id}")
async def get_plant(plant_id: str, current_user: User = Depends(get_current_user)):
    if current_user.admin:
        try:
            queried_sensor = await engine.find_one(Plant, Plant.id == plant_id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

        return jsonable_encoder(queried_sensor)
    else:
        raise HTTPException(status_code=403, detail="You are not allowed to access this endpoint")


@router.post("/plants/")
async def create_plant(plant_input: PlantInput, current_user: User = Depends(get_current_user)):
    if current_user.admin:
        plant = Plant(
            name=plant_input.name,
            description=plant_input.description,
            key=str(uuid.uuid4()),
            state=False,
            temperatures=[],
            humidities=[],
            moistures=[],
            light_values=[]
        )

        try:
            created_sensor = await engine.save(plant)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

        return jsonable_encoder(created_sensor)
    else:
        raise HTTPException(status_code=403, detail="You are not allowed to access this endpoint")


@router.delete("/plants/{plant_id}")
async def delete_plant(plant_id: str, current_user: User = Depends(get_current_user)):
    if current_user.admin:
        try:
            await engine.remove(Plant, Plant.id == plant_id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

        return jsonable_encoder({
            "message": "Successfully deleted the required plant and it's data.",
            "code": "200"
        })
    else:
        raise HTTPException(status_code=403, detail="You are not allowed to access this endpoint")


# [url]/plants/listen/[_id]?token=""

@router.websocket("/plants/listen/{plant_id}")
async def listen_plant(
        websocket: WebSocket,
        plant_id: str,
        token: str = Query(..., alias="token"),
        manager: WebSocketManager = Depends(get_socket_manager)
):
    try:
        user = await get_current_user(token)

        if not user.admin:
            await websocket.close(code=1008, reason="User is not an admin")
            return

        await manager.connect(websocket, plant_id)
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            manager.disconnect(websocket, plant_id)
    except HTTPException as e:
        await websocket.close(code=403, reason="The authentication token is expired or not valid")
        return
