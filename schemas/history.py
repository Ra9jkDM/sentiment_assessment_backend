from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

class Text_history(BaseModel):
    username: EmailStr
    date: datetime = None
    text: str = Field(min_length=1)

    positive: int = Field(default=0, ge=0, le=1)
    negative: int = Field(default=0, ge=0, le=1)
    unknown: int = Field(default=0, ge=0, le=1)

class Table_history(BaseModel):
    username: EmailStr
    date: datetime = None
    file: int = Field(ge=1)

    positive: int = Field(default=0, ge=0)
    negative: int = Field(default=0, ge=0)
    unknown: int = Field(default=0, ge=0)