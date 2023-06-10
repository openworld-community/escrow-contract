from pydantic import BaseModel, Field


class Sign(BaseModel):
    address: str = Field(min_length=42, max_length=42,
                         description="EVM address")
    signature: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "address": "0x71C7656EC7ab88b098defB751B7401B5f6d8976F",
                "signature": "0xf9a5fdaee8b647bc391f4ef71d0e436d53f3f49085219346c11db972d39c26b1",
            }
        }


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    address: str | None = None
