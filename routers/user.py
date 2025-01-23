from fastapi import APIRouter
from dependencies import loginDepends
from services import user
from schemas.user_schemas import UserSchema
from response_status import ResponseStatus


router = APIRouter()

@router.get('/user')
async def info(username: loginDepends):
    current_user = await user.get_user(username)

    if current_user:
       return current_user
    raise HTTPException(500, 'Can not get user')

@router.post('/user/update')
async def update(username: loginDepends, user_info: UserSchema):
   if await user.update_user(user_info, username):
      return ResponseStatus.success
   else:
      return ResponseStatus.failure

@router.post('/user/change_password')
async def change_password(username: loginDepends, password: str):
   if await user.update_password(username, password):
      return ResponseStatus.success
   else:
      return ResponseStatus.failure
