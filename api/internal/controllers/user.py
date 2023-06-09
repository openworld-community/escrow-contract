import os
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends, status
from ..db import user
from ..models.user import User, CreateUser
from ..models.auth import Sign

from ..auth.jwt import authenticate_user, create_access_token, get_current_user


router = APIRouter(
    prefix="/user",
    tags=["user"],
    dependencies=[],
)


@router.post("/")
async def create_user(create_user: CreateUser) -> User:
    old_user = await user.find_by_address(create_user.address)
    if old_user is not None:
        return old_user
    return await user.create(create_user)


@router.get("/nonce/{address}")
async def get_nonce(address: str):
    usr = await user.find_by_address(address)
    if usr is None:
        raise HTTPException(status_code=404, detail="User not found")
    await user.update_nonce(address)
    return {"address": address, "nonce": usr.nonce}


@router.post("/auth")
async def login_for_access_token(sig: Sign):
    user = await authenticate_user(sig)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(
        minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")))
    access_token = create_access_token(
        data={"sub": user.address}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user
