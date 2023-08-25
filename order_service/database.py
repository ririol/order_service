from fastapi import Depends
import aiopg

from config import DB_HOST,DB_NAME,DB_PASS,DB_USER, DB_PORT

DSN = f'dbname={DB_NAME} user={DB_USER} password={DB_PASS} host={DB_HOST} port={DB_PORT}'

async def get_database_pool() -> aiopg.Pool:
    pool = await aiopg.create_pool(DSN) # type: ignore
    return pool

async def close_database_pool(pool: aiopg.Pool) -> None:
    pool.close()
    await pool.wait_closed()

async def get_db(pool: aiopg.Pool = Depends(get_database_pool)) -> aiopg.Connection:
    conn = await pool.acquire()
    return conn

async def release_db(conn: aiopg.Connection, pool: aiopg.Pool = Depends(get_database_pool)) -> None:
    pool.release(conn)