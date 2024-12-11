from helpers.converters import to_model, to_sql
from repositories import users
from schemas.user_schemas import UserSchema

from schemas import user_schemas

async def get_user(username):
    user = await users.get_user(username)
    if user:
        user = to_model(user_schemas.UserSchema, user)
        return user