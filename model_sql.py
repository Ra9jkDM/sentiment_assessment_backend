from __future__ import annotations
import asyncio

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine, async_sessionmaker
# from sqlalchemy import create_engine, Column, Integer, Float, String, Date, ForeignKey, select, Boolean
# from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship, mapped_column, Mapped, relationship, backref


from typing import List
from datetime import datetime, date

from os import environ


from sqlmodel import Field, Session, SQLModel, create_engine, select, Relationship, Integer, String, Column



USERNAME = environ.get("database_username") 
PASSWORD = environ.get("database_password")

HOST = environ.get("database_host")
PORT = int(environ.get("database_port"))

DATABASE = environ.get("database_name")
DIALECT = environ.get("database_dialect")


ENGINE = AsyncEngine(create_engine(f"{DIALECT}://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}", future=True, echo=False))


# Base = declarative_base()
new_session = async_sessionmaker(ENGINE, expire_on_commit=False)


# class User(SQLModel, table=True):
#     # __tablename__ = "user"
    
#     id: int = Field(sa_column = Column(Integer, primary_key=True, unique=True))
#     username: str = Field(sa_column = Column(String(100), unique=True, nullable=False))
#     # password: Mapped[String] = mapped_column(String(100), nullable=False)
#     # salt: Mapped[String] = mapped_column(String(30), nullable=False)
    
#     # firstname: Mapped[String] = mapped_column(String(100), nullable=False)
#     # lastname: Mapped[String] = mapped_column(String(100), nullable=True)
#     # is_active: Mapped[Boolean] = mapped_column(Boolean, default=True)
#     role_id: int = Field(foreign_key='role.id')
    
#     role: "Role" = Relationship(back_populates="users")
    
# class Role(SQLModel, table=True):
#     # __tablename__ = "role"
    
#     id: int = Field(sa_column=Column(Integer, primary_key=True, unique=True))
#     name: str = Field(sa_column=Column(String(25), unique=True))
    
#     users: list[User] = Relationship(back_populates="role")

class Role(SQLModel, table=True):
    id: int = Field(sa_column=Column(Integer, primary_key=True, unique=True))
    name: str = Field(sa_column=Column(String(25), unique=True))
    
    users: list["User"] = Relationship(back_populates="role")
    
class User(SQLModel, table=True):
    id: int = Field(sa_column = Column(Integer, primary_key=True, unique=True))
    username: str = Field(sa_column = Column(String(100), unique=True, nullable=False))
    role_id: int = Field(foreign_key='role.id')
    
    role: Role = Relationship(back_populates="users")


# class HeroTeamLink(SQLModel, table=True):
#     team_id: int | None = Field(default=None, foreign_key="team.id", primary_key=True)
#     hero_id: int | None = Field(default=None, primary_key=True)
#     is_training: bool = False

#     team: "Team" = Relationship(back_populates="hero_links")
	
# class Team(SQLModel, table=True):
#     id: int | None = Field(default=None, primary_key=True)
#     name: str = Field(index=True)
#     headquarters: str

#     hero_links: list[HeroTeamLink] = Relationship(back_populates="team")

async def create_test_data():
    async with AsyncSession(ENGINE, expire_on_commit=False) as db:
        db.add(Role(name="Admin"))
        db.add(Role(name="User"))
        await db.commit()
        
        db.add(User(username='bob@mail.com', password='12odd', salt='g', firstname='Bob', lastname='Devid', role_id=2))
        db.add(User(username='ann@mail.com', password='9nw', salt='c', firstname='Ann', role_id=2))
        
        await db.commit()
        x = await db.execute(select(User))
        x = x.all()
        print(x, type(x[0]), )
        
async def main():
    async with ENGINE.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
    
    await create_test_data()
    
async def get_session():
    async with new_session() as session:
        yield session  
    
if __name__ == "__main__":
    asyncio.run(main())
    
# relationship https://sqlmodel.tiangolo.com/tutorial/many-to-many/link-with-extra-fields/?h=field#update-link-model
# convert x to pydantic type