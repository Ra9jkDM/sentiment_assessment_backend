from os import environ
import pytest
import asyncio

environ['app_mode'] = 'test'
url = 'http://127.0.0.1:8000/api/'
# export app_mode=test
# python main.py

user = {
        "username": 'vov@giv.comv',
        "firstname": "Test",
        "lastname": "test_v3",
        "role": "user",
        "password": 'secure_pass001',
        "is_active": True
    }

from models.model import create_db,  ENGINE
from models.storage_model import delete_all
from models.cache_model import delete_all_keys, client

async def _create_all():
    await create_db() # SQLAlchemy
    await delete_all() # MinIO
    await client(delete_all_keys)() # Redis

def recreate():
    asyncio.run(_create_all())


if __name__ == '__main__':
    # asyncio.run(create())
    recreate()
    # print(dir(ENGINE))
    print(ENGINE.url)
