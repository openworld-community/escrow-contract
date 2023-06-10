import os
from typing import Annotated
from fastapi import (
    APIRouter,
    Depends,
    WebSocket,
    WebSocketDisconnect,
    Query,
    HTTPException
)
from pydantic import BaseModel, Field

from ..models.user import User
from ..models.msg import UserMessage
from ..auth.jwt import get_current_user_ws, get_current_user
from ..db import escrow as escrowdb
from ..db import msg as msgdb
from ..dependencies import web3 as w3

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)


@router.get("/test")
def test(user: Annotated[User, Depends(get_current_user)]):
    return f"hello {user.address}"


class UserConnect():
    def __init__(self, ws, user):
        self.ws = ws
        self.user = user
        ws: WebSocket
        user: User


active_rooms: dict[str, list[UserConnect] | None] = dict()


@router.websocket("/join/{escrow_addr}")
async def join_to_chat_room(
    *,
    ws: WebSocket,
    escrow_addr: str,
    token: str = Query(...)
):
    await ws.accept()

    user = await get_current_user_ws(token)
    if user is None:
        await ws.close(code=1008)

    escrow_addr = escrow_addr.lower()

    escrow = await escrowdb.find_by_address(escrow_addr)
    if escrow is None:
        await ws.close(code=1008)

    c = w3.eth.contract(address=w3.toChecksumAddress(
        escrow_addr), abi=os.getenv("ESCROW_ABI"))

    seller = c.functions.seller().call().lower()
    buyer = c.functions.buyer().call().lower()
    arbiter = c.functions.arbiter().call().lower()

    print(f"""
    escrow: {escrow.address}
    seller: {seller}
    buyer: {buyer}
    arbiter: {arbiter}
    """)

    if user.address.lower() not in (seller, buyer, arbiter):
        await ws.close(code=1008)

    uc = UserConnect(ws=ws, user=user)

    if escrow_addr not in active_rooms:
        active_rooms[escrow_addr] = [uc]
    else:
        active_rooms[escrow_addr].append(uc)

    room = active_rooms[escrow_addr]

    try:
        while True:
            data: UserMessage = await uc.ws.receive_json()
            await msgdb.create(data)
            for con in room:
                await con.ws.send_json(data)
    except WebSocketDisconnect:
        print(f"User {user.address} was disconnected from room {escrow_addr}")


@router.get("/{escrow_addr}")
async def get_messages(
    escrow_addr: str,
    user: Annotated[User, Depends(get_current_user)]
):
    try:
        checksummed = w3.toChecksumAddress(escrow_addr)

        c = w3.eth.contract(address=checksummed, abi=os.getenv("ESCROW_ABI"))

        seller = c.functions.seller().call().lower()
        buyer = c.functions.buyer().call().lower()
        arbiter = c.functions.arbiter().call().lower()

        if user.address.lower() not in (seller, buyer, arbiter):
            raise HTTPException(status_code=403, detail="Forbiden")
        
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Bad address") from exc

    return await msgdb.get_by_room(escrow_addr)
