from fastapi import FastAPI
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.schemas.item import ItemIn
from core.schemas.order import OrderIn

from core.models.database import AsyncSessionLocal
from core.models.models import Item, Order


async def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()

app = FastAPI()


@app.get('/orders/')
async def list_orders():
    pass


@app.get('/orders/{id}')
async def get_single_order(id: int):
    pass

@app.post('/orders')
async def create_order():
    pass

@app.put('/orders/')
async def update_order():
    pass

@app.delete('/orders/{id}')
async def delete_order(id: int):
    pass


@app.get('/orders/{order_id}/items')
async def list_items(order_id: int):
    pass

@app.get('/orders/{order_id}/items/{item_id}')
async def get_single_item(order_id: int, item_id: int):
    pass

@app.post('/orders/{order_id}/items')
async def add_item_to_order(order_id: int):
    pass

@app.put('/orders/{order_id}/items/{item_id}')
async def update_item_in_order(order_id: int, item_id: int):
    pass

@app.delete('/orders/{order_id}/items/{item_id}')
async def delete_item_from_order(order_id: int, item_id: int):
    pass

     
@app.get('/items/')
async def get_all_items(db: AsyncSession = Depends(get_db)):
    user = await db.execute(select(Item))
    return user