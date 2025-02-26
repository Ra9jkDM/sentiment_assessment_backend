from enum import Enum
from repositories import history, users_storage

class HistoryType(Enum):
    text = 'text'
    table = 'table'

async def get_records(username, history_type, page, amount, name, start_date, end_date):
    page = page -1

    if page < 0:
        page=0

    if history_type == HistoryType.text:
        return await history.get_text_records(username, page, amount, name, start_date, end_date)
    elif history_type == HistoryType.table:
        return await history.get_table_records(username, page, amount, name, start_date, end_date)

async def get_amount(username, history_type, name, start_date, end_date):
    if history_type == HistoryType.text:
        return await history.get_amount_of_text_records(username, name, start_date, end_date)
    elif history_type == HistoryType.table:
        return await history.get_amount_of_table_records(username, name, start_date, end_date)

async def get_file(username, _id):
    return await users_storage.get_table(username, _id)

async def delete(username, _id, history_type):
    if history_type == HistoryType.text:
        return await history.delete_text(username, _id)
    elif history_type == HistoryType.table:
        return await history.delete_table(username, _id)
