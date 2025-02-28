from fastapi import APIRouter
import services.login as users
from schemas.user_schemas import UserLoginModel
from dependencies import authCookie
from fastapi.responses import JSONResponse
from dependencies import authCookie
from response_status import ResponseStatus

router = APIRouter()

@router.post('/login')
async def login(login_user: UserLoginModel):
    result = await users.login(login_user)
    if result:
        res = JSONResponse(content={**ResponseStatus.success, 'cookie': result['cookie'], 'role': result['role']})
        res.set_cookie(key=result['key'], value=result['cookie'], max_age=result['max_age'],
                           expires=result['expires'])
        return res
    return ResponseStatus.failure

@router.get('/logout')
async def logout(auth: authCookie):
    await users.logout(auth)
    res = JSONResponse(content=ResponseStatus.success)
    return res