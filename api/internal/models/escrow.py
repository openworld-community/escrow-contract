from pydantic import BaseModel, Field


class Escrow(BaseModel):
    address: str = Field(max_length=42, min_length=42,
                         description="EVM address of Escrow contract")
