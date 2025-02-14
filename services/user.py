from helpers.converters import to_model, to_sql
from repositories import users, users_storage
from repositories import cookie
from schemas.user_schemas import UserSchema
from services.registration import create_password_and_salt
from schemas import user_schemas
from helpers.encoder_session_cookies import encode as encode_username

async def get_user(username):
    user = await users.get_user(username)
    if user:
        user = to_model(user_schemas.UserSchema, user)
        return user

async def get_photo(username):
    return await users_storage.get_photo(username)

async def update_photo(username, image):
    return await users_storage.update_photo(username, image)

async def delete_photo(username):
    return await users_storage.delete_photo(username)

async def update_user(user_info, username):
    return await users.update_user(user_info, username)

async def update_password(username, password):
    password, salt = create_password_and_salt(password)
    return await users.update_password(username, password, salt)

async def delete_account(username):
    if await users.delete_account(username):
        user = encode_username(username).split('.')[0]
        await cookie.delete_all_startswith(user+'.*')
        await users_storage.delete_user(username)
    
    return True
