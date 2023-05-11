# app/routers/sensors.py
import uuid

from fastapi import APIRouter, HTTPException, Depends

from auth import get_current_user
from database import iot
from inputs.sensor_input import SensorInput
from json_encoder import jsonable_encoder
from models.sensor import Sensor
from models.user import User

router = APIRouter()


@router.post("/sensors/create")
async def create_sensor(sensor_input: SensorInput, current_user: User = Depends(get_current_user)):
    sensor = Sensor(
        name=sensor_input.name,
        description=sensor_input.description,
        key=str(uuid.uuid4()),
        temperatures=[],
        humidities=[],
        moistures=[],
        light_values=[]
    )

    new_sensor_dict = sensor.to_mongo().to_dict()

    try:
        new_sensor = await iot['sensors'].insert_one(new_sensor_dict)
        created_sensor = await iot['sensors'].find_one({"_id": new_sensor.inserted_id})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

    return jsonable_encoder(created_sensor)
