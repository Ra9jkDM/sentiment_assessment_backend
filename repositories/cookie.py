from models import cache_model
from models.cache_model import client

@client
async def create_cookie(client, id, cookie):
    await cache_model.set_json(client, id, cookie)

@client
async def get_cookie(client, id):
    return await cache_model.get_json(client, id)

@client
async def delete_cookie(client, id):
    await cache_model.delete(client, id)

@client
async def delete_all_startswith(client, pattern):
    keys = await cache_model.get_keys(client, pattern)

    for i in keys:
        await cache_model.delete(client, i.decode('utf8'))