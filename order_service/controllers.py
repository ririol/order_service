from aiopg import Connection
from fastapi import HTTPException

from schemas import OrderIn, OrderInDB, ItemIn, ItemInDB, Statistic


class OrderController:
    
    @classmethod
    async def get_all_orders(cls, db: Connection) -> list[OrderInDB]:
        async with db.cursor() as cur:
            stmt = '''SELECT ROW_TO_JSON(o) AS order_json, JSON_AGG(i.*) AS items
                    FROM "order" o
                    LEFT JOIN item i ON o.id = i.order_id
                    GROUP BY o.id
                    ORDER BY o.id;
                    '''
            await cur.execute(stmt)
            db_order_list: list[tuple[dict, list[ItemInDB]]] = await cur.fetchall()
            print(db_order_list)
            list_orders = []
            for order in db_order_list:
                item_list = order[1] if all(order[1]) else []
                list_orders.append(OrderInDB(**order[0], items=item_list))

        return list_orders


    @classmethod
    async def get_single_order(cls, id: int, db: Connection) -> OrderInDB:
        async with db.cursor() as cur:
            stmt =f'''
                    SELECT ROW_TO_JSON(o) AS order_json, JSON_AGG(i.*) AS items
                    FROM "order" o
                    LEFT JOIN item i ON o.id = i.order_id
                    WHERE o.id = {id}
                    GROUP BY o.id;
                    '''
            await cur.execute(stmt)
            db_order = await cur.fetchall()
            if not db_order: 
                raise HTTPException(status_code=404, detail=f"Order with id {id} not found")
            
            item_list = db_order[0][1] if all(db_order[0][1]) else []
            order = OrderInDB(**db_order[0][0], items=item_list)
            
        return order


    @classmethod
    async def create_order(cls, order: OrderIn, db: Connection) -> OrderInDB:   
        async with db.cursor() as cur:
            stmt = f'''
                    INSERT INTO "order" (title)
                    VALUES ('{order.title}')
                    RETURNING id;
                    '''
            await cur.execute(stmt)
            order_id: int = (await cur.fetchall())[0][0]
            
            if order.items:
                values = [(item.name, item.price, item.number, order_id) for item in order.items]
                formated_values = str(values)[1:-1]
                stmt = f'''
                        INSERT INTO item (name, price, number, order_id) 
                        VALUES {formated_values};
                        '''
                await cur.execute(stmt)
            new_order = await cls.get_single_order(order_id, db)
            
        return new_order


    @classmethod
    async def update_order(cls, id: int, order: OrderIn, db: Connection) -> OrderInDB:
        async with db.cursor() as cur:
            order_in_db = await cls.get_single_order(id, db=db)
            
            if not order_in_db: 
                raise HTTPException(status_code=404, detail=f"Order with id {id} not found")
            
            stmt = f'''
                    UPDATE public."order"
                    SET title='{order.title}'
                    WHERE id = {id};
                    '''
            await cur.execute(stmt)
            
            if order.items:
                values = [(item.name, item.price, item.number, id) for item in order.items]
                formated_values = str(values)[1:-1]
                stmt = f'''
                    INSERT INTO public.item (name, price, number, order_id)
                    VALUES {formated_values}
                    ON CONFLICT (order_id, name, price) DO UPDATE
                    SET number = EXCLUDED.number
                '''
                await cur.execute(stmt)
        updated_order = await cls.get_single_order(id, db=db)
        
        return updated_order


    @classmethod
    async def delete_order(cls, id: int, db: Connection):
        async with db.cursor() as cur:
            await cur.execute(f'''
                            DELETE FROM public."order" WHERE id = {id}
                            ''')


    @classmethod
    async def list_items(cls, order_id: int, db: Connection) -> list[ItemInDB]:
        async with db.cursor() as cur:
            stmt = f'''
                    SELECT ROW_TO_JSON(item.*)
                    FROM item
                    WHERE order_id = {order_id};
                    '''
            await cur.execute(stmt)
            result: list[tuple[dict]] = await cur.fetchall()
            list_of_items = [ItemInDB(**item[0]) for item in result]
    
        return list_of_items


    @classmethod
    async def get_single_item(cls, order_id: int, item_id: int, db: Connection) -> ItemInDB:
        async with db.cursor() as cur:
            order_in_db = await cls.get_single_order(order_id, db=db)
            if not order_in_db: 
                raise HTTPException(status_code=404, detail=f"Order with id {id} not found")
            stmt = f'''
                    SELECT ROW_TO_JSON(item.*) 
                    FROM item
                    WHERE order_id = {order_id} and id = {item_id};
                    '''
            await cur.execute(stmt)
            result: list[tuple[dict]] = await cur.fetchall()
            if not result[0][0]: 
                raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found")
            item = ItemInDB(**result[0][0])
            
        return item


    @classmethod
    async def add_item_to_order(cls, order_id: int, items: list[ItemIn], db: Connection) -> list[ItemInDB]:
        async with db.cursor() as cur:
            order_in_db = await cls.get_single_order(order_id, db=db)
            if not order_in_db: 
                raise HTTPException(status_code=404, detail=f"Order with id {order_id} not found")
            if not items: 
                raise HTTPException(status_code=404, detail=f"The items list can't be empty")
            
            values = [(item.name, item.price, item.number, order_id) for item in items]
            formated_values = str(values)[1:-1]
            stmt = f'''
                    INSERT INTO public.item (name, price, number, order_id)
                    VALUES {formated_values}
                    ON CONFLICT (order_id, name, price) DO UPDATE
                    SET number = EXCLUDED.number
                    RETURNING item.id;
                    '''
            await cur.execute(stmt)
            result: list[tuple[int]] = (await cur.fetchall())
            # could be optimized
            list_of_items = [await cls.get_single_item(order_id, item_id, db) for item_id in result[0]]
            
        return list_of_items


    @classmethod
    async def update_item_in_order(cls, order_id: int, item_id: int, item: ItemIn, db: Connection) -> ItemInDB:
        async with db.cursor() as cur:
            order_in_db = await cls.get_single_order(order_id, db=db)
            if not order_in_db: 
                raise HTTPException(status_code=404, detail=f"Order with id {order_id} not found")
            
            item_in_order = await cls.get_single_item(order_id, item_id, db=db)
            if not item_in_order: 
                raise HTTPException(status_code=404, detail=f"Item with id {order_id} not found")
            stmt = f'''
                    UPDATE public.item
                    SET name='{item.name}', price={item.price}, "number"={item.number}
                    WHERE id = {item_id};
                    '''
            await cur.execute(stmt)
            updated_item = await cls.get_single_item(order_id, item_id, db=db)
            
        return updated_item


    @classmethod
    async def delete_item_from_order(cls, order_id: int, item_id: int, db: Connection):
        async with db.cursor() as cur:
            await cur.execute(f'''
                                DELETE FROM public.item WHERE id = {item_id};
                            ''')


class StatisticController:
    
    @classmethod
    async def get_statisic(cls, db: Connection):
        async with db.cursor() as cur:
            stmt = '''SELECT ROW_TO_JSON(statistic) AS order_statistics
                      FROM (
                          SELECT 
                              COUNT(o.id)   AS total_orders,
                              SUM(o.total)  AS total_order_price,
                              AVG(o.total)  AS avg_order_price,
                              SUM(i.number) AS total_items,
                              AVG(i.number) AS avg_items,
                              (
                                  SELECT
                                      i.name
                                  FROM
                                      public.item i
                                  GROUP BY
                                      i.name
                                  ORDER BY
                                      SUM(i."number") DESC
                                  LIMIT 1
                              ) AS most_popular_item
                          FROM public."order" o
                          INNER JOIN public.item i ON o.id = i.order_id
                      ) AS statistic;
                      '''
            await cur.execute(stmt)
            result: list[tuple[dict]] = await cur.fetchall()
            statistic = Statistic(**result[0][0])

        return statistic