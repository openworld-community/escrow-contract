from .client import database as db
from ..models.user import User

user_collection = db.user


async def find_by_address(addr: str) -> User | None:
    dto = await user_collection.find_one({"address": addr})
    if dto is not None:
        return User(**dto)
    return None
