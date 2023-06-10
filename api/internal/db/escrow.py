from .client import database as db
from ..models.escrow import Escrow

ec = db.escrows


async def find_by_address(addr: str) -> Escrow | None:
    escrow = await ec.find_one({"address": addr.lower()})
    if escrow is not None:
        return Escrow(address=escrow["address"])
    return None


async def create(addr: str) -> Escrow:
    created = await ec.insert_one({"address": addr.lower()})
    return Escrow(address=created.address)
