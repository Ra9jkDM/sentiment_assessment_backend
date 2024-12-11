from fastapi import APIRouter
from schemas.ml_schemas import OneText
from services.ml import native_bias
from dependencies import loginDepends

router = APIRouter()

@router.post('/native_bias')
async def predict(username: loginDepends, text: OneText):
    pred = native_bias.predict(text.text)
    return pred