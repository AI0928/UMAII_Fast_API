from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated
from pymysql.err import IntegrityError
from pymysql.constants import ER

import api.schemas.order as order_schema
import api.cruds.order as order_crud
from api.models import order as order_model
import api.schemas.user as user_schema

from api.db import get_db
from api.settings import get_settings

from datetime import datetime, timedelta

router = APIRouter()

#全ての注文を表示する
@router.get("/orders", response_model=List[order_schema.Order])
async def list_orders(db: AsyncSession = Depends(get_db)):
    return await order_crud.get_orders(db)

#注文追加
@router.post("/orders", response_model=user_schema.User)
async def create_order(
    order_body: order_schema.OrderCreate,
    db: AsyncSession = Depends(get_db)
):
    return await order_crud.create_order(db, order_body)

@router.get("/orders/recommed", response_model=None)
async def recommed_order(
    db: AsyncSession = Depends(get_db)
):
    return await order_crud.recommend(db)