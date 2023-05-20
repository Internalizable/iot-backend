# app/routers/users.py
import hashlib

from fastapi import APIRouter, HTTPException
from starlette import status

from database import iot
from inputs.login_input import LoginRequest, SignUpRequest
from utils.auth import get_user, create_access_token
from utils.json_encoder import jsonable_encoder

router = APIRouter()


@router.post("/users/login")
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


@router.post("/users/signup")
async def create_user(signup_request: SignUpRequest):
    hashed_password = hashlib.sha256(signup_request.password.encode()).hexdigest()

    new_user_data = {
        "email": signup_request.email,
        "password": hashed_password,
        "admin": 0
    }

    new_user = await iot["users"].insert_one(new_user_data)
    created_user = await iot["users"].find_one({"_id": new_user.inserted_id})
    #todo return auth token
    return jsonable_encoder(created_user)
