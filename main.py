from typing import Annotated
from fastapi import FastAPI, Request, HTTPException, Response, Cookie, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pydantic import parse_obj_as
from typing import List
import uvicorn

import model
from model import User

app = FastAPI()

sessionDepends = Annotated[model.AsyncSession, Depends(model.get_session)]

class UserLoginModel(BaseModel):
    username: str
    password: str
    
class UserSchema(BaseModel):
    id: int
    username: str
    password: str
    salt: str
    firstname: str
    lastname: str | None
    is_active: bool
    
@app.post('/login')
async def login(user: UserLoginModel):
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
async def info(id: Annotated[str, Depends(is_login)], session: sessionDepends):
    query = model.select(model.User)
    result = await session.execute(query)
    users = result.all()
    for i in users:
        print(i) # users[0].username
    print(users, dir(users[0]), users[0]._to_tuple_instance())
    return 0
    # users = parse_obj_as(UserSchema, users)
    # return list(users)#{'info': {'name': "Bob", "id":"98"}, 'users': users}

@app.get('/info_add')
async def info(id: Annotated[str, Depends(is_login)], session: sessionDepends):
    session.add(UserSchema(id=101, username='ann1@mail.com', password='9nw', 
                           salt='c', lastname='__', firstname='Ann', is_active=False))
    await session.commit()
    return {'status': 'success'}

if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)
    
# try https://sqlmodel.tiangolo.com/tutorial/create-db-and-table/#engine-database-url
# from sqlmodel import Field, SQLModel
# https://github.com/fastapi/sqlmodel