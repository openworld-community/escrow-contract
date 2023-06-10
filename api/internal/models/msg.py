from pydantic import BaseModel, Field

class UserMessage(BaseModel):
    room: str = Field(min_length=42, max_length=42)
    usr_from: str
    text: str
