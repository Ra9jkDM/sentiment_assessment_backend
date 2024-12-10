from fastapi import APIRouter
from dependencies import loginDepends
from services import user


router = APIRouter()

@router.get('/user')
async def info(username: loginDepends):
    current_user = await user.get_user(username)

    if current_user:
       return current_user
    raise HTTPException(500, 'Can not get user')