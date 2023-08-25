from aiopg import Connection
from fastapi import APIRouter, Depends

from core.schemas.statistics import Statistic
from core.models.database import get_db

statistic_router = APIRouter(tags=['statistic'])


@statistic_router.get('/statistic')
async def get_statistic(db: Connection = Depends(get_db)):
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
                  ) AS statistic;'''
        await cur.execute(stmt)
        result = await cur.fetchall()
        statistic = Statistic(**result[0][0])

    return statistic