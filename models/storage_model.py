import asyncio
from miniopy_async import Minio
from miniopy_async.deleteobjects import DeleteObject
import aiohttp
from os import environ
import io
from enum import Enum

HOST = environ.get("s3_host")
PORT = environ.get("s3_port")
BUCKET = environ.get("s3_bucket")

# generate in MimIO web console [localhost/access-keys]
ACCESS_KEY = environ.get("s3_access_key")
SECRET_KEY = environ.get("s3_secret_key")
SECURE = int(environ.get("s3_secure")) # Http -> False[0], Https -> True[1]

class Storage(Enum):
    profile = 'profile'
    data = 'data'

def client(func):
    async def wrapper(*args, **kwargs):
        client = Minio(f"{HOST}:{PORT}",
                access_key = ACCESS_KEY,
                secret_key = SECRET_KEY,
                secure = SECURE)
        async with aiohttp.ClientSession() as session:
            return await func(client, session, *args, **kwargs)
    return wrapper

# structure
# {username}/profile # фото профиля и другая инфа о пользователе
#           /data    # .csv файлы, которые пользователь загружал на проверку


async def profile_upload(username, name, data):
    await _upload_object(f'{username}/{Storage.profile.value}', name, data)

async def profile_get(username, name):
    return await _get_object(f'{username}/{Storage.profile.value}/{name}')

async def profile_delete(username, name):
    return await _delete_object(f'{username}/{Storage.profile.value}/{name}')

async def data_upload(username, name, data):
    await _upload_object(f'{username}/{Storage.data.value}', name, data)

async def data_get(username, name):
    return await _get_object(f'{username}/{Storage.data.value}/{name}')

async def data_delete(username, name):
    return await _delete_object(f'{username}/{Storage.data.value}/{name}')

async def delete_user(username):
    return await _recursive_delete(username)

@client
async def _upload_object(client, session, path, name, data):
    await client.put_object(bucket_name = BUCKET, object_name = f"{path}/{name}",
                        data = data, length = -1, part_size=10*1024*1024,)

@client
async def _get_object(client, session, name):
    response = await client.get_object(bucket_name = BUCKET, object_name = name, session=session)
    return response

@client
async def _delete_object(client, session, name):
    await client.remove_object(bucket_name = BUCKET, object_name = name)

@client
async def _recursive_delete(client, session, name):
    objects = map(
        lambda x: DeleteObject(x.object_name),
        await client.list_objects(bucket_name = BUCKET, prefix = f'{name}/', recursive=True),
    )
    
    return await client.remove_objects(bucket_name = BUCKET, delete_object_list=objects)


async def main():
    # await _upload_object('data', 'text.txt', io.BytesIO(b'12380HHH'))
    # obj = await _get_object('data/text.txt')
    # print(obj)

    await profile_upload('ad.v_@mail.com', 'img.png', io.BytesIO(b'12380HHH'))
    print(await profile_get('ad.v_@mail.com', 'img.png'))
    print(Storage.profile.value, Storage.data)

    # print(dir(Minio))
    # await delete_user('123U')


if __name__ == "__main__":
    asyncio.run(main())