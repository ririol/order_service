from aiopg import Connection
from fastapi import APIRouter, Depends

from database import get_db
from schemas import OrderIn, OrderInDB, ItemIn, ItemInDB, Statistic
from controllers import OrderController, StatisticController

order_router = APIRouter(tags=['Order'])


@order_router.get('/orders/')
async def list_orders(db: Connection = Depends(get_db)) -> list[OrderInDB]:
    try:
        list_of_orders= await OrderController.get_all_orders(db)
    except Exception as e:
        raise e
         
    return list_of_orders


@order_router.get('/orders/{id}')
async def get_single_order(id: int, db: Connection = Depends(get_db)) -> OrderInDB:
    try:
        order = await OrderController.get_single_order(id, db)
    except Exception as e:
        raise e
    
    return order


@order_router.post('/orders/')
async def create_order(order: OrderIn, db: Connection = Depends(get_db)) -> OrderInDB:
    try:
        new_order = await OrderController.create_order(order, db)
    except Exception as e:
        raise e
    
    return new_order


@order_router.put('/orders/{id}')
async def update_order(id: int, order: OrderIn, db: Connection = Depends(get_db)) -> OrderInDB:
    try:
        updated_order = await OrderController.update_order(id, order, db)
    except Exception as e:
        raise e
    
    return updated_order


@order_router.delete('/orders/{id}', status_code=204)
async def delete_order(id: int, db: Connection = Depends(get_db)):
    try:
        await OrderController.delete_order(id, db)
    except Exception as e:
        raise e


@order_router.get('/orders/{order_id}/items')
async def list_items(order_id: int, db: Connection = Depends(get_db)) -> list[ItemInDB]:
    try:
        list_of_items = await OrderController.list_items(order_id, db)
    except Exception as e:
        raise e
    
    return list_of_items


@order_router.get('/orders/{order_id}/items/{item_id}')
async def get_single_item(order_id: int, item_id: int, db: Connection = Depends(get_db)) -> ItemInDB:
    try:
        item = await OrderController.get_single_item(order_id, item_id, db)
    except Exception as e:
        raise e
    
    return item


@order_router.post('/orders/{order_id}/items')
async def add_items_to_order(order_id: int, items: list[ItemIn], db: Connection = Depends(get_db)) -> list[ItemInDB]:
    try:
        item = await OrderController.add_item_to_order(order_id, items, db)
    except Exception as e:
        raise e
    
    return item
 

@order_router.put('/orders/{order_id}/items/{item_id}')
async def update_item_in_order(order_id: int, item_id: int, item: ItemIn, db: Connection = Depends(get_db)) -> ItemInDB:
    try:
        updated_item = await OrderController.update_item_in_order(order_id, item_id, item, db)
    except Exception as e:
        raise e
    
    return updated_item


@order_router.delete('/orders/{order_id}/items/{item_id}', status_code=204)
async def delete_item_from_order(order_id: int, item_id: int, db: Connection = Depends(get_db)):
    try:
        await OrderController.delete_item_from_order(order_id, item_id, db)
    except Exception as e:
        raise e


statistic_router = APIRouter(tags=['statistic'])


@statistic_router.get('/statistic')
async def get_statistic(db: Connection = Depends(get_db)) -> Statistic:
    try:
        statistic = await StatisticController.get_statisic(db)
    except Exception as e:
        raise e

    return statistic