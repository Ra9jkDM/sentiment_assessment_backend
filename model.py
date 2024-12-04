from __future__ import annotations

from sqlalchemy import create_engine, Column, Integer, Float, String, Date, ForeignKey, select, Boolean
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


ENGINE = create_engine(f"{DIALECT}://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")


Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True)
    username: Mapped[String] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[String] = mapped_column(String(100), nullable=False)
    salt: Mapped[String] = mapped_column(String(30), nullable=False)
    
    firstname: Mapped[String] = mapped_column(String(100), nullable=False)
    lastname: Mapped[String] = mapped_column(String(100))
    is_active: Mapped[Boolean] = mapped_column(Boolean, default=True)
    
    # role: Mapped["Role"] = relationship()
    
def create_test_data():
    with Session(autoflush=True, bind=ENGINE) as db:
        db.add(User(username='bob1@mail.com', password='12odd', salt='g', firstname='Bob', lastname='Devid'))
        db.commit()
        
def main():
    Base.metadata.create_all(bind=ENGINE)
    
    create_test_data()
    
if __name__ == "__main__":
    main()