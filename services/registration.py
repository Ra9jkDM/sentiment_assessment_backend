from helpers.converters import to_model, to_sql
from repositories import users
from schemas.user_schemas import UserRegistrationSchema
import model
from helpers.password_hasher import create_new_hash

async def create_user(new_user: UserRegistrationSchema):
    user = to_sql(model.User, new_user)
    user.password, user.salt = create_new_hash(new_user.password)
    return await users.create_user(user)


