from .client import database as db
from ..models.user import User, CreateUser
from ..utils.utils import generate_random_nonce

user_collection = db.user


async def find_by_address(addr: str) -> User | None:
    dto = await user_collection.find_one({"address": addr.lower()})
    if dto is not None:
        return User(**dto)
    return None


async def create(create_user: CreateUser) -> User:
    user = {
        "address": create_user.address.lower(),
        "nonce":  generate_random_nonce(),
        "username": create_user.username
    }
    created = await user_collection.insert_one(user)
    new_user = await user_collection.find_one({"_id": created.inserted_id})
    return User(**new_user)


async def update_nonce(address: str):
    user = await user_collection.find_one({"address": address.lower()})
    if user is None:
        raise ValueError(f"user with address {address} not found")
    await user_collection.update_one(
        {"_id": user["_id"]}, {"$set": {"nonce": generate_random_nonce()}}
    )
