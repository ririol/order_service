from fastapi import APIRouter, status

from order_service.src.database import conn_db
from order_service.src.ordering.schemas import (
    OrderIn,
    OrderInDB,
    ItemIn,
    ItemInDB,
    Statistic,
)
from order_service.src.ordering.controllers import OrderController, StatisticController

order_router = APIRouter(tags=["Order"])


@order_router.get("/orders/")
async def list_orders() -> list[OrderInDB]:
    list_of_orders = await OrderController.get_all_orders(conn_db)

    return list_of_orders


@order_router.get("/orders/{id}")
async def get_single_order(
    id: int,
) -> OrderInDB:
    order = await OrderController.get_single_order(id, conn_db)

    return order


@order_router.post("/orders/")
async def create_order(
    order: OrderIn,
) -> OrderInDB:
    new_order = await OrderController.create_order(order, conn_db)

    return new_order


@order_router.put("/orders/{id}")
async def update_order(
    id: int,
    order: OrderIn,
) -> OrderInDB:
    updated_order = await OrderController.update_order(id, order, conn_db)

    return updated_order


@order_router.delete("/orders/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    id: int,
):
    await OrderController.delete_order(id, conn_db)


@order_router.get("/orders/{order_id}/items/")
async def list_items(
    order_id: int,
) -> list[ItemInDB]:
    list_of_items = await OrderController.list_items(order_id, conn_db)

    return list_of_items


@order_router.get("/orders/{order_id}/items/{item_id}")
async def get_single_item(
    order_id: int,
    item_id: int,
) -> ItemInDB:
    item = await OrderController.get_single_item(order_id, item_id, conn_db)

    return item


@order_router.post("/orders/{order_id}/items/")
async def add_items_to_order(
    order_id: int,
    items: list[ItemIn],
) -> list[ItemInDB]:
    item = await OrderController.add_items_to_order(order_id, items, conn_db)

    return item


@order_router.put("/orders/{order_id}/items/{item_id}")
async def update_item_in_order(
    order_id: int,
    item_id: int,
    item: ItemIn,
) -> ItemInDB:
    updated_item = await OrderController.update_item_in_order(
        order_id, item_id, item, conn_db
    )

    return updated_item


@order_router.delete("/orders/{order_id}/items/{item_id}", status_code=204)
async def delete_item_from_order(
    order_id: int,
    item_id: int,
):
    await OrderController.delete_item_from_order(order_id, item_id, conn_db)


statistic_router = APIRouter(tags=["statistic"])


@statistic_router.get("/statistic/")
async def get_statistic() -> Statistic:
    statistic = await StatisticController.get_statisic(conn_db)

    return statistic
