from fastapi import APIRouter, UploadFile
from schemas.ml_schemas import OneText
from dependencies import loginDepends
from response_status import ResponseStatus
from repositories.users_storage import save_table
from services.ml import lstm_model

router = APIRouter(prefix='/lstm')

@router.post('/')
async def predict(username: loginDepends, text: OneText):
    pred = lstm_model.predict(text.text)
    return pred

@router.post('/table')
async def predict_table(username: loginDepends, file: UploadFile):
    return ''



