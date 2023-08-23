from sqlalchemy import URL

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

from order_service.config import DB_HOST,DB_NAME,DB_PASS,DB_USER, DB_PORT


DATABASE_URL = f'postgresql+aiopg://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'
DSN = f'dbname={DB_NAME} user={DB_USER} password={DB_PASS} host={DB_HOST} port={DB_PORT}'

class Base(AsyncAttrs, DeclarativeBase):
    pass

