import redis_model
from redis_model import client

@client
async def create_cookie(client, id, cookie):
    await redis_model.set_json(client, id, cookie)

@client
async def get_cookie(client, id):
    return await redis_model.get_json(client, id)

@client
async def delete_cookie(client, id):
    await redis_model.delete(client, id)
