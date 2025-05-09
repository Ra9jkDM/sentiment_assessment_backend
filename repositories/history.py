from models.model import session, User
from sqlalchemy import select, func
from schemas.history import Text_history_user, Table_history_user
from models import model
from helpers.repo_converters import to_model, from_model
import datetime

from models import cache_model
from models.cache_model import client

REDIS_TABLE_KEY = 'table_history:{}'


@to_model(Text_history_user)
@session
async def get_text_records(session, username, page, amount, name, start_date, end_date):
    _type = model.Text_history
    start = (_type.date >= start_date) if start_date else True
    end = (_type.date <= end_date + datetime.timedelta(days=1)) if end_date else True

    sel = select(_type).where((_type.username == username) & (_type.text.ilike(f'%{name}%') &
    start & end)) \
                .order_by(_type.date.desc()) \
                .offset(page*amount).limit(amount)
    obj = await session.execute(sel)
    obj = obj.scalars().all()
    return obj
    # return await _get_records(session, model.Text_history, username, page, amount)

@session
async def get_amount_of_text_records(session, username, name, start_date, end_date):
    _type = model.Text_history
    start = (_type.date >= start_date) if start_date else True
    end = (_type.date <= end_date + datetime.timedelta(days=1)) if end_date else True

    sel = select(func.count()).where((_type.username == username) & (_type.text.ilike(f'%{name}%') &
    start & end)) 
    obj = await session.execute(sel)
    obj = obj.scalars().first()
    return obj
    # return await get_amount_of_records(session, model.Text_history, username)

@session
async def get_amount_of_table_records(session, username, name, start_date, end_date):
    _type = model.Table_history
    start = (_type.date >= start_date) if start_date else True
    end = (_type.date <= end_date + datetime.timedelta(days=1)) if end_date else True

    sel = select(func.count()).where((_type.username == username) & (_type.name.ilike(f'%{name}%') &
    start & end)) 
    obj = await session.execute(sel)
    obj = obj.scalars().first()
    return obj
    # return await get_amount_of_records(session, model.Table_history, username)

async def get_amount_of_records(session, _type, username):
    query = select(func.count()).where(_type.username == username)
    result = await session.execute(query)
    result = result.scalars().first()
    return result


@to_model(Table_history_user)
@session
async def get_table_records(session, username, page, amount, name, start_date, end_date):
    _type = model.Table_history
    start = (_type.date >= start_date) if start_date else True
    end = (_type.date <= end_date + datetime.timedelta(days=1)) if end_date else True

    sel = select(_type).where((_type.username == username) & (_type.name.ilike(f'%{name}%') &
    start & end)) \
                .order_by(_type.date.desc()) \
                .offset(page*amount).limit(amount)
    obj = await session.execute(sel)
    obj = obj.scalars().all()
    return obj
    # return await _get_records(session, model.Table_history, username, page, amount)


async def _get_records(session, _type ,username, page, amount):
    sel = select(_type).where(_type.username == username) \
                .order_by(_type.date.desc()) \
                .offset(page*amount).limit(amount)
    obj = await session.execute(sel)
    obj = obj.scalars().all()
    return obj





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
        

@session
async def delete_text(session, username, _id):
    return await delete(session, model.Text_history, username, _id)

@session
async def delete_table(session, username, _id):
    return await delete(session, model.Table_history, username, _id)

async def delete(session, _type, username, _id):
    try:
        sel = select(_type).where((_type.username == username) & 
        (_type.id == _id)) 
        obj = await session.execute(sel)
        obj = obj.scalars().first()

        if obj:
            await session.delete(obj)
            await session.commit()
        return True
    except:
        return False