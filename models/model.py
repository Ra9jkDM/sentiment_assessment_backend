from __future__ import annotations
import asyncio


from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncAttrs
from sqlalchemy import create_engine, Column, Integer, Float, String, Date, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship, mapped_column, Mapped, relationship, backref, selectinload
from sqlalchemy import create_engine, CheckConstraint, func, select

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

    text_history: Mapped[List["Text_history"]] = relationship('Text_history', back_populates='user', cascade="all, delete", passive_deletes=True)
    table_history: Mapped[List["Table_history"]] = relationship('Table_history', back_populates='user', cascade="all, delete", passive_deletes=True)

    def __setitem__(self, key, value):
        setattr(self, key, value)

class Role(Base, AsyncAttrs):
    __tablename__ = 'role'

    id: Mapped[String] = mapped_column(String, primary_key=True, unique=True, nullable=False)
    name: Mapped[String] = mapped_column(String(30), nullable=False)

    users: Mapped[List['User']] = relationship('User', back_populates='role_info')


class Results:
    username: Mapped[String] = mapped_column(ForeignKey('user.username', ondelete="CASCADE"))
    id: Mapped[Integer] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    positive: Mapped[Integer] = mapped_column(Integer, nullable=False, default=0)
    negative: Mapped[Integer] = mapped_column(Integer, nullable=False, default=0)
    unknown: Mapped[Integer] = mapped_column(Integer, nullable=False, default=0)


class Text_history(Results, Base, AsyncAttrs):
    __tablename__ = 'text_history'

    text: Mapped[String] = mapped_column(String, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="text_history")

class Table_history(Results, Base, AsyncAttrs):
    __tablename__ = 'table_history'
    name: Mapped[String] = mapped_column(String, nullable=False)
    file: Mapped[Integer] = mapped_column(Integer, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="table_history")
    
    

# Example: type: Mapped[String] = mapped_column(String, CheckConstraint("type IN ('text', 'table')"))


async def create_test_data():
    async with AsyncSession(ENGINE, expire_on_commit=False) as db:
        db.add(Role(id='admin', name='Администратор'))
        db.add(Role(id='user', name='Пользователь'))

        db.add(User(username='bob@mail.com', password='12odd', salt='g', firstname='Bob', lastname='Devid', role='admin'))
        db.add(User(username='bob1@mail.com', password='12odd', salt='g', firstname='Bob', lastname='Devid', role='admin'))
        db.add(User(username='bob2@mail.com', password='12odd', salt='g', firstname='Bob', lastname='Devid', role='admin'))
        db.add(User(username='ann@mail.com', password='9nw', salt='c', firstname='Ann', role='user'))

        db.add(Text_history(username='bob@mail.com', text='test 123', positive=1))
        db.add(Text_history(username='bob@mail.com', text='te@@@hedf', negative=1))
        db.add(Table_history(username='bob@mail.com', name='file_1.xlsx', file=1, negative=10, positive=1))

        db.add(Text_history(username='ann@mail.com', text='test 123', positive=1))
        db.add(Text_history(username='ann@mail.com', text='te@@@hedf', negative=1))
        db.add(Table_history(username='ann@mail.com', name='file_2.xlsx', file=1, negative=10, positive=1))
        db.add(Table_history(username='ann@mail.com', name='file_new(1).xlsx', file=2, negative=3, positive=60, unknown=10))
        
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
    # simple_main()