from helpers.converters import to_model, to_sql
from repositories import users
from schemas.user_schemas import UserRegistrationSchema, UserDTO
from helpers.password_hasher import create_new_hash

async def create_user(new_user: UserRegistrationSchema):
    password, salt = create_new_hash(new_user.password)
    user = new_user.dict()
    user.update({"password":password, "salt": salt})
    user = UserDTO(**user)

    return await users.create_user(user)


