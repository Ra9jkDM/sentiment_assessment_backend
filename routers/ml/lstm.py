from fastapi import APIRouter, UploadFile
from schemas.ml_schemas import OneText
from dependencies import loginDepends
from response_status import ResponseStatus
from repositories.users_storage import save_table
from services.ml import lstm_model

router = APIRouter(prefix='/lstm')

@router.post('/')
async def predict(username: loginDepends, text: OneText):
    return await lstm_model.predict(text.text)
    # pred = lstm_model.predict(text.text)
    # return pred

@router.post('/table')
async def predict_table(username: loginDepends, file: UploadFile):
    ext = file.filename.split('.')[-1]
    if ext in ['csv', 'xlsx']:
        json_data, file = await lstm_model.predict_table(file, ext)
        if file:
            pass #save ....

        return json_data
    #     # print(dir(file))
    #     ## -------- ToDo -----
    #     # connect to db and store this '1.xlsx' and plain text preds in it
    #     # await save_table(username, '1.xlsx', file)
    #     return '???'
    else:
        return {**ResponseStatus.failure, 'desc': 'Wrong file type. Required: csv, xlsx'}



# ToDo:
# 1 Save to DB psql as history
# 2 save to MinIO file

