from typing import Annotated
from fastapi import Cookie, Depends, HTTPException
from schemas.redis_cookie_schemas import RedisCookieInfo
from helpers.converters import str_to_date
import datetime
from urllib.parse import unquote

import model
from repositories import cookie

authCookie = Annotated[str | None, Cookie()]

async def is_login(auth: authCookie):
    obj = await cookie.get_cookie(unquote(auth))

    if obj:
        obj = RedisCookieInfo(**obj)
        if str_to_date(obj.expire) > datetime.datetime.utcnow():
            return obj.username
    raise HTTPException(403, 'Not authorized')


loginDepends = Annotated[str, Depends(is_login)]