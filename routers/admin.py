from typing import Annotated
from fastapi import APIRouter, Body
from dependencies import loginDepends, adminDepends
from response_status import ResponseStatus
from services import admin
from schemas.user_schemas import UserRegistrationSchema

router = APIRouter(prefix='/admin')

@router.get('/users')
async def get_users(username: adminDepends, page: int, name: str = ''): # search by name
    return await admin.get_users(page, name)

@router.post('/users/create')
async def create_user(username: adminDepends, new_user: UserRegistrationSchema):
    if await admin.create_user(new_user):
        return ResponseStatus.success
    return ResponseStatus.failure

@router.post('/users/update')
async def update_user(username: adminDepends, user: UserRegistrationSchema):
    if await admin.update_user(user):
        return ResponseStatus.success
    return ResponseStatus.failure

@router.post('/users/delete')
async def delete_user(username: adminDepends, user: Annotated[str, Body()]):
    result = await admin.delete_user(user)
    
    if result:
        return ResponseStatus.success
    return ResponseStatus.failure

@router.post('/users/activate')
async def activate_user(username: adminDepends, user: Annotated[str, Body()], is_active: Annotated[bool, Body()]):
    result = await admin.activate_deactivate_user(user, is_active)
    
    if result:
        return ResponseStatus.success
    return ResponseStatus.failure


# ToDo can edit/delete users + activate/deactivate
# + 3 functions