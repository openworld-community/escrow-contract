from fastapi import APIRouter, HTTPException
from ..utils.utils import generate_random_nonce
from ..db.user import find_by_address
from ..models.user import User


router = APIRouter(
    prefix="/user",
    tags=["user"],
    dependencies=[],
)

@router.get("/nonce/{address}")
async def get_nonce(address: str):
    user = await find_by_address(address)
    if user is not None:
        return user
    raise HTTPException(status_code=404, detail="User not found")
