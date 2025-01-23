from fastapi import APIRouter
from schemas.user_schemas import UserRegistrationSchema
from services import registration as reg
from response_status import ResponseStatus

router = APIRouter()

@router.post('/registration')    
async def registration(new_user: UserRegistrationSchema):
    if await reg.create_user(new_user):
        return ResponseStatus.success
    else:
        return ResponseStatus.failure