import asyncio
import emcache
import json


def client(func):
    async def wrapper(*args, **kwargs):
        client = await emcache.create_client([emcache.MemcachedHostAddress('localhost', 11211)])
        return await func(client, *args, **kwargs)
        await client.close()
    return wrapper

async def set_data(client, key, value):
    await client.set(key.encode('utf-8'), value.encode('utf-8'))

async def get_data(client, key):
    result = await client.get(key.encode('utf-8'))
    if result:
        return result.value.decode('utf-8')

async def set_json(client, key, json_data):
    await set_data(client, key, json.dumps(json_data))

async def get_json(client, key):
    data = await get_data(client, key)
    if data:
        return json.loads(data)
    
async def delete(client, key):
    result = await client.get(key.encode('utf-8'))
    if result: # if key in db
        await client.delete(key.encode('utf-8'))


async def main():
    await client(set_data)('x1', 'abc123')
    print(await client(get_data)('x21'))
    print(await client(get_data)('x1'))
    await client(delete)('x1')
    print(await client(get_data)('x1'))
    

    await client(set_json)('x2', {'name': 'Bob'})
    print(await client(get_json)('x2'))

if __name__ == "__main__":
    asyncio.run(main())