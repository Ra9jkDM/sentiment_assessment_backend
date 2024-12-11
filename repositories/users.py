from model import session, User
from schemas.user_schemas import UserDTO
from helpers.converters import to_model, to_sql

# Test
import redis_model
from redis_model import client

def cache(func):
    @client
    async def wrapper(client, *args, **kwargs):
        print(args[0])
        result = await redis_model.get_json(client, args[0])
        if not result:
            result = await func(*args, **kwargs)
            await redis_model.set_json(client, args[0], result.dict())
            return result
        else:
            return UserDTO(**result)
    return wrapper
## Test

# ToDo: add convertation to cookieDTO in repos

def to_user(func):
    async def wrapper(*args, **kwargs):
        user = await func(*args, **kwargs)
        if user:
            user = to_model(UserDTO, user)
            return user
    return wrapper

@session
async def create_user(session, user):
    session.add(user)

    try:
        await session.commit()
        return True
    except:
        return False

@cache
@to_user
@session
async def get_user(session, username):
    return await session.get(User, username)

