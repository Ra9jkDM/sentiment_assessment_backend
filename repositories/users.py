from models.model import session, User
from schemas.user_schemas import UserDTO, UserRegistrationSchema
from sqlalchemy import select, func
from models import model
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

@to_model(UserRegistrationSchema)
@session
async def get_users(session, amount, page, name):
    sel = select(User).where(User.username.ilike(f'%{name}%')).offset(amount * page).limit(amount)
    objs = await session.execute(sel)
    objs = objs.scalars().all()
    return objs

@session
async def get_amount_of_users(session, name):
    sel = select(func.count()).where(User.username.ilike(f'%{name}%'))
    objs = await session.execute(sel)
    objs = objs.scalars().first()
    return objs

@session
async def activate_deactivate_user(session, username, is_active):
    try:
        user = await session.get(User, username)

        if user:
            user.is_active = is_active
        else:
            return False
        
        await session.commit()
        return True
    except:
        return False

@session
async def update_user(session, user_info, username):
    try:
        user = await session.get(User, username)
        updated_user = user_info.model_dump()
        for i in updated_user.keys():
            if i != 'username' or i!= 'role':
                user[i] = updated_user[i]

        await session.commit()

        return True
    except:
        return False

@session
async def update_full_user(session, user, salt, update_password=False):
    try:
        db_user = await session.get(User, user.username)

        updated_user = user.model_dump()
        for i in updated_user.keys():
            if i != 'username' and i != 'password':
                db_user[i] = updated_user[i]

        if update_password:
            db_user.password = user.password
            db_user.salt = salt

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
