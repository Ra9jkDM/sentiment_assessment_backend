from fastapi import APIRouter, UploadFile
from schemas.ml_schemas import OneText
from services.ml import native_bias
from dependencies import loginDepends
from response_status import ResponseStatus
from repositories.users_storage import save_table

router = APIRouter(prefix='/native_bias')

@router.post('/')
async def predict(username: loginDepends, text: OneText):
    pred = native_bias.predict(text.text)
    return pred

@router.post('/table')
async def predict_table(username: loginDepends, file: UploadFile):
    # predict all
    # upload file with predictions to minIO
    ext = file.filename.split('.')[-1]
    if ext in ['csv', 'xlsx']:
        file, result = native_bias.predict_table(file, ext)
        # print(dir(file))
        ## -------- ToDo -----
        # connect to db and store this '1.xlsx' and plain text preds in it
        await save_table(username, '1.xlsx', file)
        return result
    else:
        return {**ResponseStatus.failure, 'desc': 'Wrong file type. Required: csv, xlsx'}

