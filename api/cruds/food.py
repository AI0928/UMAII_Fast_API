from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from pymysql.constants import ER

import api.models.food as food_model
import api.schemas.food as food_schema

from typing import List, Tuple, Optional
from sqlalchemy import select
from sqlalchemy.engine import Result


#create_food
async def create_food( #引数の型を指定する
    db: AsyncSession, 
    food_create: food_schema.FoodCreate 
) -> food_model.Food: #返り値はfood_model.Food型を返す
    #food_model.Foodのインスタンスを生成することでDBに追加できるようにする
    #food_create.dict()は辞書型を返す
    #**food_create.dict()はキーと値をそれぞれ引数に展開する
    #例）food_create.dict()が{id:1, name:"food_name"} のような辞書型だった場合
    #food = food_model.Food(id=1, name="food_name")のように展開される
    food = food_model.Food(**food_create.dict()) 
    db.add(food) #DBに追加
    #awaitをつけるとdb.commit()が完了するまでプログラムは進まない
    await db.commit() #変更を保存
    await db.refresh(food) #一時データのリフレッシュ（よくわからない…）
    return food
    
#update_food
async def update_food(
    #引数の型
    db: AsyncSession,
    food_create: food_schema.FoodCreate,
    original: food_model.Food
) -> food_model.Food:
    original.name = food_create.name
    db.add(original)
    await db.commit()
    await db.refresh(original)
    return original

#get_foods
async def get_foods(db: AsyncSession) -> List[Tuple[int, str]]:
    result: Result = await ( #Result型宣言：SQL クエリの実行結果を表現する
        #db操作
        db.execute(
            #select文
            select(
                food_model.Food.id,
                food_model.Food.name
            )
        )
    )
    return result.all() #selectの結果をすべて取得

#任意のfoodを取得
async def get_food(
    db: AsyncSession, 
    food_id: int
) -> Optional[food_model.Food]:
    result: Result = await db.execute(
        select(food_model.Food).filter(food_model.Food.id == food_id)
    )
    food: Optional[Tuple[food_model.Food]] = result.first()
    return food[0] if food is not None else None

#delete_food
async def delete_food(
    db: AsyncSession,
    original: food_model.Food
) -> None:
    await db.delete(original)
    await db.commit()