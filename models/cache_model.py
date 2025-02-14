import redis.asyncio as redis
import asyncio
from os import environ
import json

password = environ.get("redis_pass") 

pool = redis.ConnectionPool(host='localhost', port=6379, password=password, db=0, protocol=3)


def client(func):
    async def wrapper(*args, **kwargs):
        client = redis.Redis.from_pool(pool)
        return await func(client, *args, **kwargs)
        await client.aclose()
    return wrapper

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

async def get_keys(redis, pattern):
    return await redis.keys(pattern) # id:* -> [b'id:9324', b'id:94erw', b'id:945690', b'id:wer']

async def set_json(redis, key, json_data):
    await set_data(redis, key, json.dumps(json_data))

async def get_json(redis, key):
    data = await get_data(redis, key)
    if data:
        return json.loads(data)
    
async def delete(redis, key):
    await redis.delete(key.encode('utf-8'))

async def incr(redis, key):
    return await redis.incr(key)
    
async def main():
    # client = redis.Redis.from_pool(pool)

    client = await get_client().__anext__()    
    await client.set('foo', 'bar')
    await client.set('n1', json.dumps({'status': 'ok РУ@'}))
    

    async with client.pipeline(transaction=True) as pipe:
        ok1, ok2 = await (pipe.set("key1", "value1").set("key2", "value2").execute())

    user = {'id': '12', 'name': "Bob"}
    await client.hset('user:1', mapping=user)
    
    # await client.delete('n1')
    print(await client.get('foo'))
    print(await client.get('foo1'))
    print(await client.get('key1'))
    print(json.loads(await client.get('n1')))

    await client.set('id:945690', 'bar3')
    await client.set('id:9324', 'bar3')
    await client.set('id:94erw', 'bar3')
    await client.set('id:wer', 'bar3')
    print(await client.get('id:945690'))

    cursor, keys = await client.scan(match='id:*')
    print('Pattern',keys , await client.mget(keys))
    print('Pattern', await client.hgetall('id:*'))

    print(await client.keys('id:*'))
    print('Counter', await client.incr('counter1'))
    await client.aclose()

if __name__ == '__main__':
    asyncio.run(main())
    