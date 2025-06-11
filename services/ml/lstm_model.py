import requests
import asyncio
import json
from response_status import ResponseStatus

# ToDo: add to config
API = 'http://127.0.0.1:8089/api/'
FAIL = {**ResponseStatus.failure, 'desc': 'API do not response'}

async def predict(text):
    try:
        req = await asyncio.to_thread(requests.post, API+'predict', 
            json={'text': text})

        data = json.loads(req.text.replace('\'', '"'))
        data.update(ResponseStatus.success)
        return data
    except:
        return FAIL

async def predict_table(file, ext):
    try:
        b = await file.read()
        file = {'upload_f.'+ext: b}
        req = await asyncio.to_thread(requests.post, API+'predict_table', files=file)
        json_data, file = _split_data(req.content)
        
        # print(json_data)
        # import pandas as pd
        # import io
        # df = pd.read_excel(io.BytesIO(file), engine="openpyxl")
        # print(df)
        json_data.update(ResponseStatus.success)
        return json_data, file
    except:
        return FAIL, None

def _split_data(data):
    sep = b'END'
    start = data.index(sep)
    json_data = json.loads(data[:start].decode('utf-8').replace('\'', '"'))
    file = data[start+len(sep):]
    return json_data, file