from model import session, User
from schemas.user_schemas import UserDTO
import model
from helpers.repo_converters import to_model, from_model


@from_model(model.User)
@session
async def create_user(session, user):
    session.add(user)

    try:
        await session.commit()
        return True
    except:
        return False


@to_model(UserDTO)
@session
async def get_user(session, username):
    return await session.get(User, username)

