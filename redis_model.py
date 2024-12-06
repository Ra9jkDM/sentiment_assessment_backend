import redis.asyncio as redis
import asyncio
from os import environ
import json

password = environ.get("redis_pass") 

pool = redis.ConnectionPool(host='localhost', port=6379, password=password, db=0, protocol=3)


async def get_client():
    client = redis.Redis.from_pool(pool)
    yield client
    await client.aclose()

# async def get_transaction():
#     client = redis.Redis.from_pool(pool)
#     async with client.pipeline(transaction=True) as pipe:
#         yield pipe
#     await client.aclose()
    
async def set_data(redis, key, value):
    await redis.set(key.encode('utf-8'), value.encode('utf-8'))

async def get_data(redis, key):
    result = await redis.get(key.encode('utf-8'))
    if result:
        return result.decode('utf-8')

async def set_json(redis, key, json_data):
    await set_data(redis, key, json.dumps(json_data))

async def get_json(redis, key):
    data = await get_data(redis, key)
    if data:
        return json.loads(data)
    
async def delete(redis, key):
    await redis.delete(key.encode('utf-8'))
    
async def main():
    client = redis.Redis.from_pool(pool)
    await client.set('foo', 'bar')
    await client.set('n1', json.dumps({'status': 'ok РУ@'}))
    
    async with client.pipeline(transaction=True) as pipe:
        ok1, ok2 = await (pipe.set("key1", "value1").set("key2", "value2").execute())

    # user = {'id': '12', 'name': "Bob"}
    # await client.hset('user:1', user)
    
    print(await client.get('foo'))
    print(await client.get('foo1'))
    print(await client.get('key1'))
    print(json.loads(await client.get('n1')))
    
    await client.aclose()

if __name__ == '__main__':
    asyncio.run(main())
    