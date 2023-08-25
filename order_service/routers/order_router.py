from aiopg import Connection
from fastapi import APIRouter, Depends

from core.schemas.item import ItemIn, ItemInDB
from core.schemas.order import OrderIn, OrderInDB
from core.models.database import get_db
from controllers import order_controller


order = APIRouter(tags=['Order'])

@order.get('/orders/')
async def list_orders(db: Connection = Depends(get_db)) -> list[OrderInDB]:
    try:
        list_of_orders= await order_controller.get_all_orders(db)
    except Exception as e:
        raise e
         
    return list_of_orders


@order.get('/orders/{id}')
async def get_single_order(id: int, db: Connection = Depends(get_db)) -> OrderInDB:
    try:
        order = await order_controller.get_single_order(id, db)
    except Exception as e:
        raise e
    
    return order


@order.post('/orders/')
async def create_order(order: OrderIn, db: Connection = Depends(get_db)) -> OrderInDB:
    try:
        new_order = await order_controller.create_order(order, db)
    except Exception as e:
        raise e
    
    return new_order


@order.put('/orders/{id}')
async def update_order(id: int, order: OrderIn, db: Connection = Depends(get_db)) -> OrderInDB:
    try:
        updated_order = await order_controller.update_order(id, order, db)
    except Exception as e:
        raise e
    
    return updated_order


@order.delete('/orders/{id}', status_code=204)
async def delete_order(id: int, db: Connection = Depends(get_db)):
    try:
        await order_controller.delete_order(id, db)
    except Exception as e:
        raise e


@order.get('/orders/{order_id}/items')
async def list_items(order_id: int, db: Connection = Depends(get_db)) -> list[ItemInDB]:
    try:
        list_of_items = await order_controller.list_items(order_id, db)
    except Exception as e:
        raise e
    
    return list_of_items


@order.get('/orders/{order_id}/items/{item_id}')
async def get_single_item(order_id: int, item_id: int, db: Connection = Depends(get_db)) -> ItemInDB:
    try:
        item = await order_controller.get_single_item(order_id, item_id, db)
    except Exception as e:
        raise e
    
    return item


@order.post('/orders/{order_id}/items')
async def add_items_to_order(order_id: int, items: list[ItemIn], db: Connection = Depends(get_db)) -> list[ItemInDB]:
    try:
        item = await order_controller.add_item_to_order(order_id, items, db)
    except Exception as e:
        raise e
    
    return item
 

@order.put('/orders/{order_id}/items/{item_id}')
async def update_item_in_order(order_id: int, item_id: int, item: ItemIn, db: Connection = Depends(get_db)) -> ItemInDB:
    try:
        updated_item = await order_controller.update_item_in_order(order_id, item_id, item, db)
    except Exception as e:
        raise e
    
    return updated_item


@order.delete('/orders/{order_id}/items/{item_id}', status_code=204)
async def delete_item_from_order(order_id: int, item_id: int, db: Connection = Depends(get_db)):
    try:
        await order_controller.delete_item_from_order(order_id, item_id, db)
    except Exception as e:
        raise e
