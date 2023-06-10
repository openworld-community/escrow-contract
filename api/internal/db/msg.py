from .client import database as db
from ..models.msg import UserMessage

msg_collection = db.msg

async def create(msg: UserMessage):
    await msg_collection.insert_one(
        {'usr_from': msg["usr_from"], 'room': msg["room"], 'text': msg["text"]}
    )

async def get_by_room(room: str) -> list[UserMessage]:
    dtos = await msg_collection.find({'room': room}).to_list(None)
    return [{'usr_from': m['usr_from'], 'room': m['room'], 'text': m['text']} for m in dtos]