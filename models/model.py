from __future__ import annotations
import asyncio


from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncAttrs
from sqlalchemy import create_engine, Column, Integer, Float, String, Date, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship, mapped_column, Mapped, relationship, backref, selectinload
from sqlalchemy import create_engine

from typing import List
from datetime import datetime, date

from os import environ



USERNAME = environ.get("database_username") 
PASSWORD = environ.get("database_password")

HOST = environ.get("database_host")
PORT = int(environ.get("database_port"))

DATABASE = environ.get("database_name")
DIALECT = environ.get("database_dialect")


ENGINE = create_async_engine(f"{DIALECT}://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")


Base = declarative_base()
new_session = async_sessionmaker(ENGINE, expire_on_commit=False)

class User(Base, AsyncAttrs):
    __tablename__ = "user"
    
    username: Mapped[String] = mapped_column(String(100), primary_key=True, unique=True, nullable=False)
    password: Mapped[String] = mapped_column(String(100), nullable=False)
    salt: Mapped[String] = mapped_column(String(30), nullable=False)
    
    firstname: Mapped[String] = mapped_column(String(100), nullable=False)
    lastname: Mapped[String] = mapped_column(String(100), nullable=True)
    is_active: Mapped[Boolean] = mapped_column(Boolean, default=True)
    
    role: Mapped[String] = mapped_column(ForeignKey('role.id', ondelete="CASCADE"))
    role_info: Mapped["Role"] = relationship("Role", back_populates="users", cascade="all, delete", passive_deletes=True)

    def __setitem__(self, key, value):
        setattr(self, key, value)

class Role(Base, AsyncAttrs):
    __tablename__ = 'role'

    id: Mapped[String] = mapped_column(String, primary_key=True, unique=True, nullable=False)
    name: Mapped[String] = mapped_column(String(30), nullable=False)

    users: Mapped[List['User']] = relationship('User', back_populates='role_info')

    
async def create_test_data():
    async with AsyncSession(ENGINE, expire_on_commit=False) as db:
        db.add(Role(id='admin', name='Администратор'))
        db.add(Role(id='user', name='Пользователь'))

        db.add(User(username='bob@mail.com', password='12odd', salt='g', firstname='Bob', lastname='Devid', role='admin'))
        db.add(User(username='bob1@mail.com', password='12odd', salt='g', firstname='Bob', lastname='Devid', role='admin'))
        db.add(User(username='bob2@mail.com', password='12odd', salt='g', firstname='Bob', lastname='Devid', role='admin'))
        db.add(User(username='ann@mail.com', password='9nw', salt='c', firstname='Ann', role='user'))
        
        await db.commit()
        x = await db.execute(select(User))
        x = x.scalars().all()
        print(x, dir(x[0]))
        print(x[0].username, x[0].role)
    
        user = await db.get(User, 'bob@mail.com')
        await db.refresh(user, attribute_names=['role_info'])
        print('Async', user.role_info.name)

        user = await db.get(User, 'ann@mail.com')
        role = await user.awaitable_attrs.role_info
        print('Async await attrs', role.name)

async def main():
    async with ENGINE.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    await create_test_data()

def simple_main(): # sync
    ENGINE = create_engine(f"postgresql+psycopg2://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")
    with Session(ENGINE) as db:
        user = db.get(User, 'bob@mail.com')
        print(user.firstname, user.role_info.name)
        role = db.get(Role, 'admin')
        for i in role.users:
            print('\t'+i.username)
    
async def get_session():
    async with new_session() as session:
        yield session  

def session(func):
    async def wrapper(*args, **kwargs):
        async with new_session() as session:
            return await func(session, *args, **kwargs)
    return wrapper
    
if __name__ == "__main__":
    asyncio.run(main())
    simple_main()