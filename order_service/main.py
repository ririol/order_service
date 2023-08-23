from fastapi import FastAPI, Depends, HTTPException


from core.models.database import DSN
from core.schemas.item import ItemIn, ItemInDB
from core.schemas.order import OrderIn, OrderInDB

import aiopg

app = FastAPI()


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

@app.on_event("startup")
async def startup_db():
    app.state.pool = await get_database_pool()

@app.on_event("shutdown")
async def shutdown_db():
    await close_database_pool(app.state.pool)


@app.get('/orders')
async def list_orders(db: aiopg.Connection = Depends(get_db)) -> list[OrderInDB]:
    async with db.cursor() as cur:
        await cur.execute('''SELECT ROW_TO_JSON(o) AS order_json, JSON_AGG(i.*) AS items
                             FROM "order" o
                             LEFT JOIN item i ON o.id = i.order_id
                             GROUP BY o.id;''')
        result = await cur.fetchall()
        list_orders = []
        for order in result:
            item_list = order[1] if all(order[1]) else []
            list_orders.append(OrderInDB(**order[0], items=item_list))
    return list_orders


@app.get('/orders/{id}')
async def get_single_order(id: int, db: aiopg.Connection = Depends(get_db)) -> OrderInDB:
    async with db.cursor() as cur:
        await cur.execute(f'''
                            SELECT ROW_TO_JSON(o) AS order_json, JSON_AGG(i.*) AS items
                            FROM "order" o
                            LEFT JOIN item i ON o.id = i.order_id
                            WHERE o.id = {id}
                            GROUP BY o.id;''')

        result = await cur.fetchall()
        if not result: raise HTTPException(status_code=404, detail=f"Order with id {id} not found")
        item_list = result[0][1] if all(result[0][1]) else []

        return OrderInDB(**result[0][0], items=item_list)


@app.post('/orders')
async def create_order(order: OrderIn, db: aiopg.Connection = Depends(get_db)) -> OrderInDB:
    total_sum = 0
    for item in order.items:
        total_sum += item.price
        
    async with db.cursor() as cur:
        await cur.execute(f'''
                            INSERT INTO "order" (title, total)
                            VALUES ('{order.title}', {total_sum})
                            RETURNING id;
                            ''')
        order_id: int = (await cur.fetchall())[0][0]
        
        if order.items:
            stmt = 'INSERT INTO item (name, price, number, order_id) VALUES\n'
            for item in order.items:
                stmt += f"('{item.name}', {item.price}, {item.number}, {order_id}),"
            stmt = stmt[:-1] + ';'
             
            await cur.execute(stmt)

        return await get_single_order(order_id, db=db)


@app.put('/orders/{id}')
async def update_order(id: int, order: OrderIn, db: aiopg.Connection = Depends(get_db)) -> OrderInDB:
    total_sum = 0
    for item in order.items:
        total_sum += item.price
        
    async with db.cursor() as cur:
        
        order_in_db = await get_single_order(id, db=db)
        if not order_in_db: raise HTTPException(status_code=404, detail=f"Order with id {id} not found")
        
        await cur.execute(f'''
                            UPDATE public."order"
	                        SET title='{order.title}',total={total_sum}, 
	                        WHERE id = {id};
                            ''')
        if order.items:
            stmt = 'UPDATE item (name, price, number, order_id) VALUES\n'
            for item in order.items:
                stmt += f"('{item.name}', {item.price}, {item.number}, {id}),"
            stmt = stmt[:-1] + ';'
             
            await cur.execute(stmt)
    
    return await get_single_order(id, db=db)


@app.delete('/orders/{id}', status_code=204)
async def delete_order(id: int, db: aiopg.Connection = Depends(get_db)):
    async with db.cursor() as cur:
        await cur.execute(f'''
                           DELETE FROM public."order" WHERE id = {id}
                          ''')


@app.get('/orders/{order_id}/items')
async def list_items(order_id: int, db: aiopg.Connection = Depends(get_db)) -> list[ItemInDB]:
    async with db.cursor() as cur:
        await cur.execute(f'''
                           SELECT ROW_TO_JSON(item.*)
                           FROM item
                           WHERE order_id = {order_id};
                          ''')
        result: list[tuple[dict]] = await cur.fetchall()
        print(result)
        list_of_items = []
        for item in result:
            list_of_items.append(ItemInDB(**item[0]))
        
        return list_of_items


@app.get('/orders/{order_id}/items/{item_id}')
async def get_single_item(order_id: int, item_id: int, db: aiopg.Connection = Depends(get_db)) -> ItemInDB:
    async with db.cursor() as cur:
        order_in_db = await get_single_order(order_id, db=db)
        if not order_in_db: raise HTTPException(status_code=404, detail=f"Order with id {id} not found")
        await cur.execute(f'''
                           SELECT ROW_TO_JSON(item.*) 
                           FROM item
                           WHERE order_id = {order_id} and id = {item_id};
                          ''')
        result: list[tuple[dict]] = await cur.fetchall()
        if not result[0][0]: raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found")
        return ItemInDB(**result[0][0])


@app.post('/orders/{order_id}/items')
async def add_item_to_order(order_id: int, item: ItemIn, db: aiopg.Connection = Depends(get_db)) -> ItemInDB:
    async with db.cursor() as cur:
        order_in_db = await get_single_order(order_id, db=db)
        if not order_in_db: raise HTTPException(status_code=404, detail=f"Order with id {order_id} not found")
        await cur.execute(f'''
                           INSERT INTO public.item(name, price, "number", order_id)
	                       VALUES ('{item.name}', {item.price}, {item.number}, {order_id})
                           RETURNING ROW_TO_JSON(item.*);
                          ''')
        result = await cur.fetchall()
        
        return ItemInDB(**result[0][0])

@app.put('/orders/{order_id}/items/{item_id}')
async def update_item_in_order(order_id: int, item_id: int, item: ItemIn, db: aiopg.Connection = Depends(get_db)) -> ItemInDB:
    pass

@app.delete('/orders/{order_id}/items/{item_id}', status_code=204)
async def delete_item_from_order(order_id: int, item_id: int, db: aiopg.Connection = Depends(get_db)):
    pass


@app.get('/items/', )
async def get_items(db: aiopg.Connection = Depends(get_db)) -> list[ItemInDB]:
    async with db.cursor() as cur:
        await cur.execute('SELECT ROW_TO_JSON(item.*) FROM item')
        result: list[tuple[dict]] = await cur.fetchall()
        print(result)
        list_of_items = []
        for item in result:
            list_of_items.append(ItemInDB(**item[0]))
    return list_of_items