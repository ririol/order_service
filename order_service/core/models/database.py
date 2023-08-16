from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


### ASYNC ###

SQLALCHEMY_DATABASE_URL = 'postgresql+asyncpg://postgres:1111@localhost/ordering_service'


engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL
)

AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass


### SYNC ###

# SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:1111@localhost/ordering_service'

# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL
# )
# AsyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base()