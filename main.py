from typing import Annotated
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from routers import login, registration, user
from routers.ml import native_bias


app = FastAPI()
router = APIRouter(prefix='/api')

router.include_router(login.router, tags=['login'])
router.include_router(registration.router, tags=['registration'])
router.include_router(user.router, tags=['user'])

ml_router = APIRouter(prefix='/ml', tags=['ml models'])

ml_router.include_router(native_bias.router)

router.include_router(ml_router)
app.include_router(router)

origins = [
    "http://localhost:4200",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

   

if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)
