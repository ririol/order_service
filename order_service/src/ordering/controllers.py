from fastapi import HTTPException
from pydantic import ValidationError
import psycopg2
from order_service.src.ordering.schemas import (
    OrderIn,
    OrderInDB,
    ItemIn,
    ItemInDB,
    Statistic,
)
from order_service.src.database import ConnectionDB


class OrderController:
    @staticmethod
    async def get_all_orders(db: ConnectionDB) -> list[OrderInDB]:
        stmt = """SELECT ROW_TO_JSON(o) AS order_json, JSON_AGG(i.*) AS items
                FROM "order" o
                LEFT JOIN item i ON o.id = i.order_id
                GROUP BY o.id
                ORDER BY o.id;
                """
        db_order_list: list[tuple[dict, list[ItemInDB]]] = await db.fetch_rows(stmt)
        list_orders = []
        for order in db_order_list:
            item_list = order[1] if all(order[1]) else []
            list_orders.append(OrderInDB(**order[0], items=item_list))

        return list_orders

    @staticmethod
    async def get_single_order(id: int, db: ConnectionDB) -> OrderInDB:
        stmt = f"""
                SELECT ROW_TO_JSON(o) AS order_json, JSON_AGG(i.*) AS items
                FROM "order" o
                LEFT JOIN item i ON o.id = i.order_id
                WHERE o.id = {id}
                GROUP BY o.id;
                """

        db_order = await db.fetch_rows(stmt)
        if not db_order:
            raise HTTPException(status_code=404, detail=f"Order with id {id} not found")

        item_list = db_order[0][1] if all(db_order[0][1]) else []
        order = OrderInDB(**db_order[0][0], items=item_list)

        return order

    @staticmethod
    async def create_order(order: OrderIn, db: ConnectionDB) -> OrderInDB:
        stmt = f"""
                INSERT INTO "order" (title)
                VALUES ('{order.title}')
                RETURNING id;
                """

        order_id: int = (await db.fetch_rows(stmt))[0][0]

        if order.items:
            values = [
                (item.name, item.price, item.number, order_id) for item in order.items
            ]
            formated_values = str(values)[1:-1]
            stmt = f"""
                    INSERT INTO item (name, price, number, order_id) 
                    VALUES {formated_values};
                    """

        new_order = await OrderController.get_single_order(order_id, db)

        return new_order

    @staticmethod
    async def update_order(id: int, order: OrderIn, db: ConnectionDB) -> OrderInDB:
        order_in_db = await OrderController.get_single_order(id, db=db)

        if not order_in_db:
            raise HTTPException(status_code=404, detail=f"Order with id {id} not found")

        await db.fetch_rows(
            f"""
                UPDATE public."order"
                SET title='{order.title}'
                WHERE id = {id};
                """
        )

        if order.items:
            values = [(item.name, item.price, item.number, id) for item in order.items]
            formated_values = str(values)[1:-1]
            await db.fetch_rows(
                f"""
                INSERT INTO public.item (name, price, number, order_id)
                VALUES {formated_values}
                ON CONFLICT (order_id, name, price) DO UPDATE
                SET number = public.item.number + EXCLUDED.number
            """
            )

        updated_order = await OrderController.get_single_order(id, db=db)

        return updated_order

    @staticmethod
    async def delete_order(id: int, db: ConnectionDB):
        await db.fetch_rows(
            f"""
            DELETE FROM public."order" WHERE id = {id}
            """
        )

    @staticmethod
    async def list_items(order_id: int, db: ConnectionDB) -> list[ItemInDB]:
        stmt = f"""
                SELECT ROW_TO_JSON(item.*)
                FROM item
                WHERE order_id = {order_id};
                """

        result: list[tuple[dict]] = await db.fetch_rows(stmt)
        list_of_items = [ItemInDB(**item[0]) for item in result]

        return list_of_items

    @staticmethod
    async def get_single_item(
        order_id: int, item_id: int, db: ConnectionDB
    ) -> ItemInDB:
        order_in_db = await OrderController.get_single_order(order_id, db=db)
        if not order_in_db:
            raise HTTPException(status_code=404, detail=f"Order with id {id} not found")
        stmt = f"""
                SELECT ROW_TO_JSON(item.*) 
                FROM item
                WHERE order_id = {order_id} and id = {item_id};
                """

        result: list[tuple[dict]] = await db.fetch_rows(stmt)
        if not result:
            raise HTTPException(
                status_code=404, detail=f"Item with id {item_id} not found"
            )
        item = ItemInDB(**result[0][0])

        return item

    @staticmethod
    async def add_items_to_order(
        order_id: int, items: list[ItemIn], db: ConnectionDB
    ) -> list[ItemInDB]:
        order_in_db = await OrderController.get_single_order(order_id, db=db)
        if not order_in_db:
            raise HTTPException(
                status_code=404, detail=f"Order with id {order_id} not found"
            )
        if not items:
            raise HTTPException(
                status_code=404, detail=f"The items list can't be empty"
            )
        values = [(item.name, item.price, item.number, order_id) for item in items]
        formated_values = str(values)[1:-1]
        stmt = f"""
                INSERT INTO public.item (name, price, number, order_id)
                VALUES {formated_values}
                ON CONFLICT (order_id, name, price) DO UPDATE
                SET number = public.item.number + EXCLUDED.number 
                RETURNING item.id;
                """

        result: list[tuple[int]] = await db.fetch_rows(stmt)
        # could be optimized
        list_of_items = [
            await OrderController.get_single_item(order_id, item_id[0], db)
            for item_id in result
        ]

        return list_of_items

    @staticmethod
    async def update_item_in_order(
        order_id: int, item_id: int, item: ItemIn, db: ConnectionDB
    ) -> ItemInDB:
        order_in_db = await OrderController.get_single_order(order_id, db=db)
        if not order_in_db:
            raise HTTPException(
                status_code=404, detail=f"Order with id {order_id} not found"
            )

        item_in_order = await OrderController.get_single_item(order_id, item_id, db=db)
        if not item_in_order:
            raise HTTPException(
                status_code=404, detail=f"Item with id {order_id} not found"
            )
        try:
            stmt = f"""
                    UPDATE public.item
                    SET name='{item.name}', price={item.price}, "number"={item.number}
                    WHERE id = {item_id}
                    """
            await db.fetch_rows(stmt)

        except psycopg2.errors.UniqueViolation:  # type: ignore
            stmt = f"""
                INSERT INTO public.item (name, price, number, order_id)
                VALUES {item.name, item.price, item.number, order_id}
                ON CONFLICT (order_id, name, price) DO UPDATE
                SET number = public.item.number + EXCLUDED.number 
                RETURNING item.id;
                DELETE FROM public.item WHERE id = {item_id};
                """
            # RETURNING item.id; i can instatly return object instead of additional api call
            # TODO: refactor all places like that
            await db.fetch_rows(stmt)

        updated_item = await OrderController.get_single_item(order_id, item_id, db=db)

        return updated_item

    @staticmethod
    async def delete_item_from_order(order_id: int, item_id: int, db: ConnectionDB):
        await db.fetch_rows(
            f"""
                DELETE FROM public.item WHERE id = {item_id};
            """
        )


class StatisticController:
    @staticmethod
    async def get_statisic(db: ConnectionDB):
        stmt = """SELECT ROW_TO_JSON(statistic) AS order_statistics
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
                    """

        result: list[tuple[dict]] = await db.fetch_rows(stmt)
        try:
            statistic = Statistic(**result[0][0])
        except ValidationError as e:
            raise HTTPException(status_code=404, detail="No objects for statistic")

        return statistic
