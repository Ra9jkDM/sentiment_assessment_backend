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


@session
async def update_user(session, user_info, username):
    try:
        user = await session.get(User, username)
        updated_user = user_info.model_dump()
        for i in updated_user.keys():
            if i != 'username':
                user[i] = updated_user[i]

        await session.commit()

        return True
    except:
        return False

@session
async def update_password(session, username, password, salt):
    try:
        user = await session.get(User, username)
        user.password = password
        user.salt = salt
        await session.commit()
        return True
    except:
        return False

@session
async def delete_account(session, username):
    # ToDo (удалить инфу в связанных таблицах)
    try:
        user = await session.get(User, username)
        if user:
            await session.delete(user)
            await session.commit()
            return True
    except:
        return False