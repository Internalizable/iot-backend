# app/routers/users.py
import hashlib

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from starlette import status

from database import engine
from inputs.login_input import LoginRequest, SignUpRequest
from models.user import User
from utils.auth import create_access_token
from utils.json_encoder import jsonable_encoder
from odmantic.exceptions import DuplicateKeyError

router = APIRouter()


@router.post("/users/login")
async def login_for_access_token(login_request: LoginRequest):
    user = await engine.find_one(User, User.email == login_request.email)
    hashed_password = hashlib.sha256(login_request.password.encode()).hexdigest()
    if not user or user.password != hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"email": user.email})

    user_dict = {
        "id": str(user.id),  # convert ObjectId to string
        "email": user.email,
        "admin": user.admin
    }

    return jsonable_encoder({"access_token": access_token, "user": user_dict})


@router.post("/users/signup")
async def create_user(signup_request: SignUpRequest):
    hashed_password = hashlib.sha256(signup_request.password.encode()).hexdigest()

    new_user = User(email=signup_request.email, password=hashed_password, admin=False)

    try:
        new_user = await engine.save(new_user)
    except DuplicateKeyError as e:
        raise HTTPException(status_code=400, detail="Email already exists")

    access_token = create_access_token(data={"email": signup_request.email})

    user_dict = {
        "id": str(new_user.id),  # convert ObjectId to string
        "email": new_user.email,
        "admin": new_user.admin
    }

    return jsonable_encoder({"access_token": access_token, "user": user_dict})
