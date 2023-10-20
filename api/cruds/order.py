from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from pymysql.constants import ER

import api.models.order as order_model
import api.schemas.order as order_schema
import api.cruds.food as food_crud
import api.schemas.food as food_schema
import api.models.food as food_model
import api.cruds.user as user_crud
import api.schemas.user as user_schema
from api.models import user as user_model

from typing import List, Tuple, Optional
from sqlalchemy import select
from sqlalchemy.engine import Result

#注文時に料理の値段分、ユーザーの料金に追加する
async def add_price(
        db: AsyncSession,
        food: food_model.Food,
        user: user_model.User
) -> user_model.User:
    user.total_price += food.price
    db.add(user)
    await db.commit()
    await db.refresh(user)
    await db.refresh(food)
    return user

#注文API
async def create_order(#引数の型を指定する
    db: AsyncSession, 
    order_create: order_schema.OrderCreate 
) -> user_model.User: #返り値
    #インスタンス生成
    # .dict()は辞書型を返す
    #**はキーと値をそれぞれ引数に展開する
    order = order_model.Order(**order_create.dict())
    db.add(order) #DBに追加
    await db.commit()
    await db.refresh(order)
    food = await food_crud.get_food(db, food_id=order.food_id)
    user = await user_crud.get_user(db, user_id=order.user_id)
    user = await add_price(db, food, user)
    return user

#一覧表示
async def get_orders(db: AsyncSession) -> List[Tuple[int, int, int]]:
    result: Result = await ( #Result型宣言：SQL クエリの実行結果を表現する
        #db操作
        db.execute(
            #select文
            select(
                order_model.Order.id,
                order_model.Order.user_id,
                order_model.Order.food_id
            )
        )
    )
    return result.all() #selectの結果をすべて取得

#削除
async def delete_order(
    db: AsyncSession,
    original: order_model.Order
) -> None:
    await db.delete(original)
    await db.commit()