from typing import Annotated
from fastapi import FastAPI, Request, HTTPException, Response, Cookie, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn


app = FastAPI()

class UserLogin(BaseModel):
    username: str
    password: str
    
@app.post('/login')
async def login(user: UserLogin):
    if user.username == 'bob' and user.password=='123':
        res = JSONResponse(content={'status': 'success'})
        res.set_cookie(key='auth', value='sess_key_1')
    else:
        res = JSONResponse(content={'status': 'failure'})
    return res

async def is_login(auth: Annotated[str | None, Cookie()] = None):
    if auth:
        return 100
    raise HTTPException(403, 'Not authorized')
    
@app.get('/logout')
async def logout(id: Annotated[str, Depends(is_login)]):
    res = JSONResponse(content={'status': 'success'})
    return res
    
@app.get('/info')
async def info(id: Annotated[str, Depends(is_login)]):
    return {'info': {'name': "Bob", "id":"98"}}

    

if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)