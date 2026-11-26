from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

from auth.jwt_handler import create_access_token

router = APIRouter()

password_hash = PasswordHash((Argon2Hasher(),))

users = {}


class User(BaseModel):
    username: str
    password: str


@router.post("/register")
def register(user: User):

    if user.username in users:
        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )

    users[user.username] = password_hash.hash(user.password)

    return {"message": "User registered successfully"}


@router.post("/login")
def login(user: User):

    if user.username not in users:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    stored_password = users[user.username]

    if not password_hash.verify(user.password, stored_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    token = create_access_token(user.username)

    return {
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer"
    }
