from helpers.converters import to_model, to_sql
from repositories import users
from schemas.user_schemas import UserRegistrationSchema, UserDTO
from helpers.password_hasher import create_new_hash

async def create_user(new_user: UserRegistrationSchema, change_role=False):
    if not change_role:
        new_user.role = 'user'

    password, salt = create_password_and_salt(new_user.password)
    user = new_user.dict()
    user.update({"password":password, "salt": salt})
    user = UserDTO(**user)

    return await users.create_user(user)

def create_password_and_salt(password):
    password, salt = create_new_hash(password)
    return password, salt
