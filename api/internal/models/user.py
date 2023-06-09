from pydantic import BaseModel, Field
from bson import ObjectId
from .common import PyObjectId


class User(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="id")
    nonce: str = Field(description="Random nonce")
    address: str = Field(..., min_length=42, max_length=42,
                         description="EVM address")
    username: str = Field(description="Username")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class CreateUser(BaseModel):
    address: str
    username: str | None
