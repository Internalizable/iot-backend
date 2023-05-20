# app/routers/plants.py
import uuid

from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.params import Query
from odmantic import ObjectId

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

        plants_collection = engine.get_collection(Plant)
        pipeline = [
            {"$project": {"name": 1, "description": 1, "key": 1, "state": 1}}
        ]

        documents = await plants_collection.aggregate(pipeline).to_list(length=None)
        queried_sensors = [Plant.parse_doc(doc) for doc in documents]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

    return jsonable_encoder(queried_sensors)


@router.get("/plants/{plant_id}")
async def get_plant(plant_id: str, current_user: User = Depends(get_current_user)):
    if current_user.admin:
        try:
            plant_id_obj = ObjectId(plant_id)

            plant = await engine.find_one(Plant, Plant.id == plant_id_obj)

            plant.temperatures.sort(key=lambda t: t.timestamp, reverse=True)
            plant.humidities.sort(key=lambda h: h.timestamp, reverse=True)
            plant.moistures.sort(key=lambda m: m.timestamp, reverse=True)
            plant.light_values.sort(key=lambda l: l.timestamp, reverse=True)
            plant.temperatures = plant.temperatures[:10]
            plant.humidities = plant.humidities[:10]
            plant.moistures = plant.moistures[:10]
            plant.light_values = plant.light_values[:10]
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

        return jsonable_encoder(plant)
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
