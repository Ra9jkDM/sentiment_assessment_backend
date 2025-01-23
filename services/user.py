from helpers.converters import to_model, to_sql
from repositories import users
from schemas.user_schemas import UserSchema
from services.registration import create_password_and_salt

from schemas import user_schemas

async def get_user(username):
    user = await users.get_user(username)
    if user:
        user = to_model(user_schemas.UserSchema, user)
        return user

async def update_user(user_info, username):
    return await users.update_user(user_info, username)

async def update_password(username, password):
    password, salt = create_password_and_salt(password)
    return await users.update_password(username, password, salt)