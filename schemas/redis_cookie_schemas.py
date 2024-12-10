from pydantic import BaseModel

class RedisCookieInfo(BaseModel):
    username: str
    expire: str