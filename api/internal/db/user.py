from .client import database as db
from ..models.user import User, CreateUserDto, UpdateUserDto
from ..utils.utils import generate_random_nonce

user_collection = db.user

async def find_by_address(addr: str) -> User | None:
    dto = await user_collection.find_one({"address": addr.lower()})
    if dto is not None:
        return User(**dto)
    return None


async def create(create_user: CreateUserDto) -> User:
    exist = await user_collection.find_one({"address": create_user.address})
    if exist is not None:
        return exist
    user: User = {
        "address": create_user.address.lower(),
        "nonce":  generate_random_nonce(),
        "username": create_user.username,
        "bio": create_user.bio,
        "telegram": create_user.telegram,
        "twitter_link": create_user.twitter_link,
        "discord_tag": create_user.discord_tag,
        "avatar": create_user.avatar
    }
    created = await user_collection.insert_one(user)
    new_user = await user_collection.find_one({"_id": created.inserted_id})
    return User(**new_user)


async def update_one(dto: UpdateUserDto) -> User:
    user = await user_collection.find_one({"address": dto.address.lower()})
    if user is None:
        raise ValueError(f"user with address {dto.address} is not found")
    await user_collection.update_one(
        {"_id": user["_id"]},
        {
            "$set": {
                "username": dto.username,
                "bio": dto.bio,
                "telegram": dto.telegram,
                "twitter_link": dto.twitter_link,
                "discord_tag": dto.discord_tag,
                "avatar": dto.avatar
            }
        }
    )
    new_user = await user_collection.find_one({"_id": user["_id"]})
    return User(**new_user)


async def update_nonce(address: str):
    user = await user_collection.find_one({"address": address.lower()})
    if user is None:
        raise ValueError(f"user with address {address} not found")
    await user_collection.update_one(
        {"_id": user["_id"]}, {"$set": {"nonce": generate_random_nonce()}}
    )
