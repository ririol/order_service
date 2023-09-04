from fastapi import FastAPI

from order_service.src.database import conn_db, DSN
from order_service.src.ordering.routers import order_router, statistic_router

app = FastAPI()
app.include_router(order_router)
app.include_router(statistic_router)


@app.on_event("startup")
async def startup_db():
    app.state.conn_db = conn_db
    app.state.pool = await app.state.conn_db.get_database_pool(DSN)


@app.on_event("shutdown")
async def shutdown_db():
    await app.state.conn_db.close_database_pool()
