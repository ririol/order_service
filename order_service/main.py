from fastapi import FastAPI

from core.models.database import get_database_pool, close_database_pool
from routers.order_router import order
from routers.statistic_router import statistic_router

app = FastAPI()
app.include_router(order)
app.include_router(statistic_router)

@app.on_event("startup")
async def startup_db():
    app.state.pool = await get_database_pool()

@app.on_event("shutdown")
async def shutdown_db():
    await close_database_pool(app.state.pool)



