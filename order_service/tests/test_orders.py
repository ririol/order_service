import asyncio
from httpx import AsyncClient

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


test_order = {
    "title": "test order",
    "items": [
        {"name": "banana", "price": 10, "number": 10},
        {"name": "apple", "price": 5, "number": 10},
    ],
}


async def test_empty_db_after_init(ac: AsyncClient):
    response = await ac.get("/orders/")
    assert response.status_code == 200
    assert response.content == b"[]"


async def test_create_order_with_empty_items(ac: AsyncClient):
    order = {"title": "test order", "items": []}
    response = await ac.post("/orders/", json=order)
    assert response.status_code == 200
    order = response.json()
    assert order["title"] == "test order"
    assert order["items"] == []
    assert order["total"] == 0


async def test_get_orders(ac: AsyncClient):
    response = await ac.get("/orders/")
    assert response.status_code == 200
    orders = response.json()
    assert len(orders) == 1


async def test_change_items_in_order(ac: AsyncClient):
    response = await ac.put(
        "/orders/2",
        json=test_order,
    )
    updated_order = response.json()
    assert updated_order["total"] == 150
    order = {
        "title": "test order",
        "items": [{"name": "apple", "price": 5, "number": 10}],
    }
    response = await ac.put(
        "/orders/2",
        json=order,
    )
    updated_order = response.json()
    assert updated_order["total"] == 200


async def test_get_order_items(ac: AsyncClient):
    response = await ac.get("/orders/2/items/")
    items = response.json()
    assert len(items) == 2
    assert items[0]["name"] == "banana"
    assert items[0]["price"] == 10
    assert items[0]["number"] == 10
    assert items[1]["name"] == "apple"
    assert items[1]["price"] == 5
    assert items[1]["number"] == 20


async def test_get_order_item(ac: AsyncClient):
    response = await ac.get("/orders/2/items/2")
    item = response.json()
    assert item["name"] == "banana"
    assert item["price"] == 10
    assert item["number"] == 10


async def test_add_items_to_order(ac: AsyncClient):
    items = [
        {"name": "apple", "price": 5, "number": 10},
        {"name": "banana", "price": 5, "number": 10},
    ]

    response = await ac.post("/orders/2/items/", json=items)
    items = response.json()
    assert items == [
        {"id": 3, "name": "apple", "price": 5, "number": 30, "order_id": 2},
        {"id": 6, "name": "banana", "price": 5, "number": 10, "order_id": 2},
    ]
    response = await ac.get("/orders/2")
    order = response.json()
    assert order["total"] == 300
    assert len(order["items"]) == 3


async def test_update_items_in_order(ac: AsyncClient):
    item = {"name": "apple", "price": 3, "number": 10}
    response = await ac.put("/orders/2/items/3", json=item)
    item = response.json()
    assert item["price"] == 3
    response = await ac.get("/orders/2")
    order = response.json()
    assert order["total"] == 180
    item = {"name": "banana", "price": 10, "number": 10}
    response = await ac.put("/orders/2/items/6", json=item)
    response = await ac.get("/orders/2")
    order = response.json()
    assert len(order["items"]) == 2
    assert order["total"] == 230


async def test_get_statistic(ac: AsyncClient):
    obj1 = {"name": "banana", "price": 10, "number": 10}
    obj2 = {"name": "apple", "price": 3, "number": 10}
    for _ in range(5):
        await ac.put("/orders/2/items/3", json=obj1)
    for _ in range(4):
        await ac.put("/orders/2/items/3", json=obj2)

    response = await ac.get("/statistic/")
    statistic = response.json()
    assert statistic == {
        "total_orders": 1,
        "total_order_price": 300,
        "avg_order_price": 300.0,
        "total_items": 30,
        "avg_items": 30.0,
        "most_popular_item": "banana",
    }


async def test_delete_item_in_order(ac: AsyncClient):
    await ac.delete("/orders/2/items/3")
    response = await ac.get("/orders/2")
    order = response.json()
    assert len(order["items"]) == 1


async def test_delete_order(ac: AsyncClient):
    await ac.delete("/orders/2")
    orders = await ac.get("/orders/")
    assert orders.status_code == 200
    assert orders.content == b"[]"
