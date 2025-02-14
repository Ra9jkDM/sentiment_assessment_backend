import models.storage_model as storage_model
from models.storage_model import profile_upload, profile_get, profile_delete, data_upload, data_get, data_delete
import io

AVATAR = 'avatar.png'

async def get_photo(username):
    data = await profile_get(username, AVATAR)
    return io.BytesIO(await data.read())

async def get_table(username, _id):
    file = await data_get(username, f'{_id}.xlsx')    
    return io.BytesIO(await file.read())

async def update_photo(username, image):
    await profile_upload(username, AVATAR, image)

async def delete_photo(username):
    await profile_delete(username, AVATAR)

async def save_table(username, name, file):
    await data_upload(username, name, file)

async def delete_user(username):
    await storage_model.delete_user(username)