from typing import Annotated
from fastapi import APIRouter, Body
from fastapi.responses import StreamingResponse
from dependencies import loginDepends
from response_status import ResponseStatus
# import repositories.history as history_rep
from services import history
import datetime

router = APIRouter(prefix='/history')

RECORD_AMOUNT_ON_PAGE = 10


@router.get('')
async def get_records(username: loginDepends, history_type: history.HistoryType, page: int, 
        name: str = '', start_date: datetime.date = None, end_date: datetime.date = None):
    res = await history.get_records(username, history_type, page, RECORD_AMOUNT_ON_PAGE, name, start_date, end_date)
    return res

@router.get('/length')
async def get_amount_of_records(username: loginDepends, history_type: history.HistoryType,
        name: str = '', start_date: datetime.date = None, end_date: datetime.date = None):
    return await history.get_amount(username, history_type, name, start_date, end_date)


@router.get('/file')
async def get_file(username: loginDepends, id: int):
    file = await history.get_file(username, id)
    return StreamingResponse(content = file, media_type='application/vnd.ms-excel')

@router.post('/delete')
async def delete_record(username: loginDepends, id: Annotated[int, Body()], history_type: Annotated[history.HistoryType, Body()]):
    print(id, history_type)
    result = await history.delete(username, id, history_type)

    if result:
        return ResponseStatus.success
    return ResponseStatus.failure
    