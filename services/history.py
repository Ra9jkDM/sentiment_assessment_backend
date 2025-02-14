from enum import Enum
from repositories import history, users_storage

class HistoryType(Enum):
    text = 'text'
    table = 'table'

async def get_records(username, history_type, page, amount):
    page = page -1
    if history_type == HistoryType.text:
        return await history.get_text_records(username, page, amount)
    elif history_type == HistoryType.table:
        return await history.get_table_records(username, page, amount)

async def get_amount(username, history_type):
    if history_type == HistoryType.text:
        return await history.get_amount_of_text_records(username)

async def get_file(username, _id):
    return await users_storage.get_table(username, _id)
