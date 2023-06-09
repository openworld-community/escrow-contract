import os
from typing import Annotated
from datetime import timedelta, datetime

from jose import jwt, JWTError
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer

from ..db import user as userdb
from ..models.auth import TokenData, Sign
from ..models.user import User
from ..utils.utils import verify_signature

ALGORITHM = "HS256"


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/auth")


async def authenticate_user(sig: Sign) -> User | bool:
    user = await userdb.find_by_address(sig.address)
    print(f"user: {user.address}")
    if not user:
        return False
    if not verify_signature(sig.address, sig.signature, sig.message):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    print("sec key:", os.getenv("SECRET_KEY"))
    encoded_jwt = jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[ALGORITHM])
        address: str = payload.get("sub")
        if address is None:
            raise credentials_exception
        token_data = TokenData(address=address)
    except JWTError as exc:
        raise credentials_exception from exc

    user = await userdb.find_by_address(token_data.address)
    if user is None:
        raise credentials_exception

    return user
