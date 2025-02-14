from fastapi import APIRouter
from dependencies import loginDepends
from response_status import ResponseStatus
import repositories.history as history_rep
from services import history

router = APIRouter(prefix='/history')

RECORD_AMOUNT_ON_PAGE = 5


@router.get('')
async def get_records(username: loginDepends, history_type: history.HistoryType, page: int):
    res = await history.get_records(username, history_type, page, RECORD_AMOUNT_ON_PAGE)
    return res

@router.get('/length')
async def get_amount_of_records(username: loginDepends, history_type: history.HistoryType):
    return await history.get_amount(username, history_type)


@router.get('/file')
async def get_file(username: loginDepends):
    pass