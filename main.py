from typing import Annotated
from fastapi import FastAPI, Request, HTTPException, Response, Cookie, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, EmailStr
from pydantic import parse_obj_as
from typing import List
import uvicorn

import model
from model import User
import datetime


from password_hasher import create_new_hash, compare_passwords
import encoder_session_cookies as session_str
import redis_model

app = FastAPI()

origins = [
    "http://localhost:4200"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

sessionDepends = Annotated[model.AsyncSession, Depends(model.get_session)]
authCookie = Annotated[str | None, Cookie()]
redisDepends = Annotated[redis_model.redis.Redis, Depends(redis_model.get_client)]

async def is_login(redis: redisDepends, auth: authCookie):
    obj = await redis_model.get_json(redis, auth)
    if obj:
        obj = RedisCookieInfo(**obj)
        if str_to_date(obj.expire) > datetime.datetime.utcnow():
            return obj.username
    raise HTTPException(403, 'Not authorized')


loginDepends = Annotated[str, Depends(is_login)]



@app.get('/logout')
async def logout(auth: authCookie, redis: redisDepends):
    await redis_model.delete(redis, auth)
    res = JSONResponse(content={'status': 'success'})
    return res

class UserLoginModel(BaseModel):
    username: EmailStr
    password: str = Field(min_length=8, max_length=100)
    
class UserSchema(BaseModel):
    username: EmailStr
    firstname: str = Field(min_length=2, max_length=100)
    lastname: str | None
    is_active: bool
    
class UserRegistrationSchema(UserLoginModel, UserSchema):
    salt: str | None = ''

class RedisCookieInfo(BaseModel):
    username: str
    expire: str
    
    
    
def to_model(target_cls: BaseModel, obj: list[model.Base] | model.Base):
    if isinstance(obj, list): 
        result = [parse_obj_as(target_cls, i.__dict__) for i in obj]
    else:
        result = parse_obj_as(target_cls, obj.__dict__)
    return result

def to_sql(target_cls: model.Base, obj):
    return target_cls(**obj.dict())    
    

@app.post('/registration')    
async def registration(session: sessionDepends, new_user: UserRegistrationSchema):
    user = to_sql(model.User, new_user)
    user.password, user.salt = create_new_hash(new_user.password)
    session.add(user)
    
    try:
        await session.commit()
        return {'status': 'success', 'user': to_model(UserSchema, user)}
    except:
        return {'status': 'failure'}
    
    
@app.post('/login')
async def login(session: sessionDepends, redis: redisDepends, login_user: UserLoginModel):
    user = await session.get(model.User, login_user.username)
    if user:
        user = to_model(UserRegistrationSchema, user)

        if compare_passwords(user.password,  login_user.password, user.salt):
            max_age, expires_date = get_coockie_expires_date()
            auth = get_auth_string(user.username)
            await save_cookie(redis, auth, user.username, expires_date)
            res = JSONResponse(content={'status': 'success', 'cookie': auth})
            res.set_cookie(key='auth', value=auth, max_age=max_age,
                           expires=expires_date)
            return res
    return {'status': 'failure'}

def date_to_str(date):
    return date.strftime("%Y-%m-%d %H:%M:%S")

def str_to_date(str_date):
    return datetime.datetime.strptime(str_date, "%Y-%m-%d %H:%M:%S")

def get_coockie_expires_date():
    max_age = 10 * 24 * 60 * 60
    expires_date = datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age)
    expires_date = date_to_str(expires_date)
    return max_age, expires_date

def get_auth_string(username):
    return session_str.encode(username)

async def save_cookie(redis, cookie, username, expires_date):
    try:
        await redis_model.set_json(redis, cookie, RedisCookieInfo(username=username, expire=expires_date).dict())
    except:
        raise HTTPException(500, 'Can not create authentication token')
    

    
@app.get('/user')
async def info(username: loginDepends, session: sessionDepends):
    user = await session.get(model.User, username)
    if user:
       user = to_model(UserSchema, user)
       return user
    raise HTTPException(500, 'Can not get user')
    

# @app.get('/info') # only for test
# async def info(username: loginDepends, session: sessionDepends):
#     query = model.select(model.User)
#     result = await session.execute(query)
#     users = result.scalars().all()
#     print(users[0].username, users[0].__dict__)
#     users = to_model(UserSchema, users)
#     user = to_model(UserSchema, users[0])
#     print(user)
#     return users
   

if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)
