from fastapi import APIRouter, UploadFile
from schemas.ml_schemas import OneText
from schemas.history import Text_history_user, Table_history_user
from dependencies import loginDepends
from response_status import ResponseStatus
from repositories.users_storage import save_table
from services.ml import lstm_model
import repositories.history as history
import io

router = APIRouter(prefix='/lstm')

@router.post('/')
async def predict(username: loginDepends, text: OneText):
    result = await lstm_model.predict(text.text)

    obj = Text_history(username=username, text=result['text'])

    predicted = result['pred']
    if predicted == 0:
        obj.negative = 1
    elif predicted == 1:
        obj.positive = 1
    else:
        obj.unknown = 1

    result = await history.save_text_pred(obj)

    if result:
        return {**ResponseStatus.success, **obj.dict()}
    else:
        return {**ResponseStatus.failure, 'desc': 'Can not save results to database'}

@router.post('/table')
async def predict_table(username: loginDepends, file: UploadFile):
    ext = file.filename.split('.')[-1]
    if ext in ['csv', 'xlsx']:
        json_data, file = await lstm_model.predict_table(file, ext)
        if file:
            table = Table_history_user(username=username, file=1, positive=json_data['positive'], 
                                    negative=json_data['negative'], unknown=json_data['unknown'])
            file_id = await history.save_table_pred(table)
            if file_id:
                await save_table(username, f'{file_id}.xlsx', io.BytesIO(file))

        return json_data
    else:
        return {**ResponseStatus.failure, 'desc': 'Wrong file type. Required: csv, xlsx'}

# Examoles:
# table
# {
#   "rows_amount": 14,
#   "positive": 5,
#   "negative": 9,
#   "unknown": 0,
#   "status": "success"
# }

# on text
# {
#   "text": "string тк текст отзыва положительно",
#   "clear_text": "тк текст отзыв положительно",
#   "pred": 0, # -1 - unknown
#   "pred_word": "negative",
#   "status": "success"
# }

