from helpers.converters import to_model, to_sql
from repositories import users, cookie
from schemas.redis_cookie_schemas import RedisCookieInfo
from helpers.password_hasher import create_new_hash, compare_passwords
import helpers.encoder_session_cookies as session_str
from helpers.converters import date_to_str
import datetime

from schemas import user_schemas


COOKIE_MAX_AGE = 10 * 24 * 60 * 60
COOKIE_KEY = 'auth'

async def login(login_user: user_schemas.UserLoginModel):
    user = await users.get_user(login_user.username)

    if not user:
        return False
    
    if compare_passwords(user.password, login_user.password, user.salt):
        max_age, expires_date = _get_coockie_expires_date()
        auth = _get_auth_string(user.username)
        status = await save_cookie(auth, user.username, expires_date)
        if status:
            return {'cookie': auth, 'max_age': max_age, 'expires': expires_date, 'key': COOKIE_KEY}
    return False

async def logout(auth_cookie):
    await cookie.delete_cookie(auth_cookie)
    return True


def _get_coockie_expires_date():
    expires_date = datetime.datetime.utcnow() + datetime.timedelta(seconds=COOKIE_MAX_AGE)
    expires_date = date_to_str(expires_date)
    return COOKIE_MAX_AGE, expires_date

def _get_auth_string(username):
    return session_str.encode(username)

async def save_cookie(cookie_, username, expires_date):
    cookie_dict = RedisCookieInfo(username=username, expire=expires_date).dict()
    await cookie.create_cookie(cookie_, cookie_dict)
    return True
