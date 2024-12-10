from model import session, User

@session
async def create_user(session, user):
    session.add(user)

    try:
        await session.commit()
        return True
    except:
        return False

@session
async def get_user(session, username):
    return await session.get(User, username)
