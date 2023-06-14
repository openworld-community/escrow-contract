from pydantic import BaseModel, Field
from bson import ObjectId
from .common import PyObjectId


class User(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="id")
    nonce: str = Field(description="Random nonce")
    address: str = Field(..., min_length=42, max_length=42,
                         description="EVM address")
    username: str | None = Field(description="Username")
    bio: str | None = Field(description="User bio")
    telegram: str | None = Field(description="User telegram")
    twitter_link: str | None = Field(description="User twitter")
    discord_tag: str | None = Field(descritpoin="User discord tag")
    avatar: str | None = Field(description="Avatar")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class CreateUserDto(BaseModel):
    address: str = Field(...)
    username: str | None
    bio: str | None = Field(description="User bio")
    telegram: str | None = Field(description="User telegram")
    twitter_link: str | None = Field(description="User twitter")
    discord_tag: str | None = Field(descritpoin="User discord tag")
    avatar: str | None = Field(description="Avatar")


class UpdateUserDto(CreateUserDto):
    pass
