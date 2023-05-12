# app/routers/users.py

from fastapi import APIRouter, HTTPException
from starlette import status

from utils.auth import get_user, create_access_token
from database import iot
from inputs.login_input import LoginRequest
from utils.json_encoder import jsonable_encoder
from models.user import User

router = APIRouter()


@router.post("/users/token")
async def login_for_access_token(login_request: LoginRequest):
    user = await get_user(login_request.email)
    if not user or user.password != login_request.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"email": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/users/")
async def create_user(user: User):
    new_user = await iot["users"].insert_one(user.dict())
    created_user = await iot["users"].find_one({"_id": new_user.inserted_id})
    return jsonable_encoder(created_user)
