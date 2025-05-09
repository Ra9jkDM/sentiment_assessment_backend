from typing import Annotated
from fastapi import APIRouter, HTTPException, File, UploadFile
from fastapi.responses import StreamingResponse
from dependencies import loginDepends
from services import user
from schemas.user_schemas import UserSchema, UserPassword
from response_status import ResponseStatus


router = APIRouter(prefix='/user')

@router.get('/')
async def info(username: loginDepends):
    current_user = await user.get_user(username)

    if current_user:
       return current_user
    raise HTTPException(500, 'Can not get user')

@router.get('/avatar')
async def photo(username: loginDepends):
   try:
      image = await user.get_photo(username)
      return StreamingResponse(content = image, media_type='image/img')
   except:
      return ResponseStatus.failure

@router.post('/avatar/update')
async def update_photo(username: loginDepends, photo: UploadFile):
   if photo.size/1024**2 < 2: # MB
      await user.update_photo(username, photo.file)
      return ResponseStatus.success
   else:
      return ResponseStatus.failure

@router.post('/avatar/delete')
async def delete_photo(username: loginDepends):
   await user.delete_photo(username)
   return ResponseStatus.success


@router.post('/update')
async def update(username: loginDepends, user_info: UserSchema):
   if await user.update_user(user_info, username):
      return ResponseStatus.success
   else:
      return ResponseStatus.failure

@router.post('/change_password')
async def change_password(username: loginDepends, password: UserPassword):
   if await user.update_password(username, password.password):
      return ResponseStatus.success
   else:
      return ResponseStatus.failure

@router.post('/delete_account')
async def delete_account(username: loginDepends):
   if await user.delete_account(username):
      return ResponseStatus.success
   else:
      return ResponseStatus.failure