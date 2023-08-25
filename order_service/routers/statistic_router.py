from aiopg import Connection
from fastapi import APIRouter, Depends

from core.models.database import get_db
from core.schemas.statistics import Statistic
from controllers import statistic_controller


statistic_router = APIRouter(tags=['statistic'])


@statistic_router.get('/statistic')
async def get_statistic(db: Connection = Depends(get_db)) -> Statistic:
    try:
        statistic = await statistic_controller.get_statisic(db)
    except Exception as e:
        raise e

    return statistic