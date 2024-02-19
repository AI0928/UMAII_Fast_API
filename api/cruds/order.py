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

from sqlalchemy import func

from sklearn.decomposition import NMF
import numpy as np

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
    
    nmf_data = result.all()
    print(len(nmf_data))
    

    return nmf_data #selectの結果をすべて取得

#削除
async def delete_order(
    db: AsyncSession,
    original: order_model.Order
) -> None:
    await db.delete(original)
    await db.commit()

async def recommend(
        db: AsyncSession
)->None:
    user_count = await db.execute(select(func.count('*')).select_from(user_model.User))
    food_count = await db.execute(select(func.count('*')).select_from(food_model.Food))

    user_count = user_count.scalar()
    food_count = food_count.scalar()

    out_array = []
    for i in range(1, user_count+1):
        in_array = []
        for l in range(1, food_count+1):
            #print(i, l)
            count = await db.execute(select(func.count('*')).select_from(order_model.Order).where((order_model.Order.user_id == i) & (order_model.Order.food_id == l)))
            count = count.scalar()
            in_array.append(count)
            #print(in_array)
        out_array.append(in_array)
        #print(out_array)
    #a = await db.execute(select(func.count('*')).select_from(order_model.Order).where((order_model.Order.user_id == 2) & (order_model.Order.food_id == 1)))
    #print('user_id:1, count:' + str(a.scalar()))
    print(out_array)
    return