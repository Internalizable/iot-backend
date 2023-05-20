# app/json_encoder.py

from odmantic.bson import ObjectId
from fastapi.encoders import jsonable_encoder as fastapi_jsonable_encoder
from typing import Any


def handle_objectid(obj: Any) -> Any:
    if isinstance(obj, ObjectId):
        return str(obj)
    return obj


def jsonable_encoder(obj, *args, **kwargs):
    if isinstance(obj, dict):
        return {key: handle_objectid(value) for key, value in obj.items()}
    return fastapi_jsonable_encoder(obj, *args, **kwargs)
