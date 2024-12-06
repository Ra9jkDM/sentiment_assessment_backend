from __future__ import annotations
import asyncio


from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine, Column, Integer, Float, String, Date, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship, mapped_column, Mapped, relationship, backref


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

class User(Base):
    __tablename__ = "user"
    
    username: Mapped[String] = mapped_column(String(100), primary_key=True, unique=True, nullable=False)
    password: Mapped[String] = mapped_column(String(100), nullable=False)
    salt: Mapped[String] = mapped_column(String(30), nullable=False)
    
    firstname: Mapped[String] = mapped_column(String(100), nullable=False)
    lastname: Mapped[String] = mapped_column(String(100), nullable=True)
    is_active: Mapped[Boolean] = mapped_column(Boolean, default=True)
    
    # role: Mapped["Role"] = relationship()

    
async def create_test_data():
    async with AsyncSession(ENGINE, expire_on_commit=False) as db:
        db.add(User(username='bob@mail.com', password='12odd', salt='g', firstname='Bob', lastname='Devid'))
        db.add(User(username='ann@mail.com', password='9nw', salt='c', firstname='Ann'))
        
        await db.commit()
        x = await db.execute(select(User))
        x = x.scalars().all()
        print(x, dir(x[0]))
        print(x[0].username)
        
async def main():
    async with ENGINE.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    await create_test_data()
    
async def get_session():
    async with new_session() as session:
        yield session  
    
if __name__ == "__main__":
    asyncio.run(main())