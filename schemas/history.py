from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

class User_data(BaseModel):
    username: EmailStr

class Date(BaseModel):
    date: datetime = None

class Text_history(Date):
    text: str = Field(min_length=1)

    positive: int = Field(default=0, ge=0, le=1)
    negative: int = Field(default=0, ge=0, le=1)
    unknown: int = Field(default=0, ge=0, le=1)

class Table_history(Date):
    file: int = Field(ge=1)

    positive: int = Field(default=0, ge=0)
    negative: int = Field(default=0, ge=0)
    unknown: int = Field(default=0, ge=0)

class Text_history_user(Text_history, User_data):
    pass

class Table_history_user(Table_history, User_data):
    pass