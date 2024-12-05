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
    username: str
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
    
def to_model(target_cls: BaseModel, obj: list[model.Base] | model.Base):
    if isinstance(obj, list): 
        result = [parse_obj_as(target_cls, i.__dict__) for i in obj]
    else:
        result = parse_obj_as(target_cls, obj.__dict__)
    return result

def to_sql(target_cls: model.Base, obj):
    return target_cls(**obj.dict())

@app.get('/info')
async def info(id: Annotated[str, Depends(is_login)], session: sessionDepends):
    query = model.select(model.User)
    result = await session.execute(query)
    users = result.scalars().all()
    print(users[0].username, users[0].__dict__)
    users = to_model(UserSchema, users)
    user = to_model(UserSchema, users[0])
    print(user)
    return users
   
@app.get('/info_add')
async def info(id: Annotated[str, Depends(is_login)], session: sessionDepends):
    user = UserSchema(username='Qann2@mail.com', lastname='Null', firstname='Rob', is_active=False)
    
    user = to_sql(model.User, user)
    user.password = 'n111'
    user.salt = 'salt1'
    
    session.add(user)
    await session.commit()
    return {'status': 'success'}

if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)
