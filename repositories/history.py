from models.model import session, User
from sqlalchemy import select
from schemas.history import Text_history
from models import model
from helpers.repo_converters import to_model, from_model

from models import cache_model
from models.cache_model import client

REDIS_TABLE_KEY = 'table_history:{}'

@from_model(model.Text_history)
@session
async def save_text_pred(session, obj):
    session.add(obj)
    
    try:
        await session.commit()
        return obj
    except:
        return False



@from_model(model.Table_history)
@session
async def save_table_pred(session, obj):
    username = obj.username
    # await _set_file_id(username, 4)
    try:
        cached_id = await _get_file_id(username)
        if cached_id <= 1:
            last_id = await _get_last_id(session, username)
            if last_id:
                cached_id = last_id.file + 1
                await _set_file_id(username, cached_id)
            else:
                await _set_file_id(username, 1)
                cached_id = 1
            
        obj.file = cached_id
        session.add(obj)
        await session.commit()
        return cached_id
    except:
        return False
    


async def _get_last_id(session, username):
    sel = select(model.Table_history).where(model.Table_history.username == username) \
                               .order_by(model.Table_history.file.desc())

    obj = await session.execute(sel)
    obj = obj.scalars().first()
    return obj

@client
async def _get_file_id(client, username):
    return await cache_model.incr(client, REDIS_TABLE_KEY.format(username))

@client
async def _set_file_id(client, username, value):
    await cache_model.set_data(client, REDIS_TABLE_KEY.format(username), str(value))
        