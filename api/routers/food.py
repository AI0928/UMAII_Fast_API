from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated
from pymysql.err import IntegrityError
from pymysql.constants import ER

import api.schemas.food as food_schema
import api.cruds.food as food_crud
from api.models import food as food_model

from api.db import get_db
from api.settings import get_settings

from datetime import datetime, timedelta

router = APIRouter()

#全ての料理を取得するAPI
#レスポンスはfood_schema.Foodのリスト型
@router.get("/foods", response_model=List[food_schema.Food])
async def list_foods(db: AsyncSession = Depends(get_db)):
    return await food_crud.get_foods(db) #全ての料理がリストで返される

#任意の料理の取得
@router.get("/foods/{food_id}", response_model=food_schema.Food)
async def get_food(
    food_id: int, 
    db: AsyncSession = Depends(get_db)):
    food = await food_crud.get_food(db, food_id=food_id)
    if food is None:
        raise HTTPException(status_code=404, detail="Food not found")
    
    return food


#料理の追加
@router.post("/foods", response_model=food_schema.FoodCreateResponse)
async def create_food(
    food_body: food_schema.FoodCreate, 
    db: AsyncSession = Depends(get_db)):
    return await food_crud.create_food(db, food_body)

#料理の更新
@router.put("/foods/{food_id}", response_model=food_schema.FoodCreateResponse)
async def update_food(
    food_id: int, 
    food_body: food_schema.FoodCreateResponse,
    db: AsyncSession = Depends(get_db)
):
    food = await food_crud.get_food(db, food_id=food_id)
    if food is None:
        raise HTTPException(status_code=404, detail="Food not found")
    
    return await food_crud.update_food(db, food_body, original=food)

#料理の削除
@router.delete("/foods/{food_id}", response_model=None)
async def delete_food(food_id: int, db: AsyncSession = Depends(get_db)):
    food = await food_crud.get_food(db, food_id=food_id)
    if food is None:
        raise HTTPException(status_code=404, detail="Food not found")
    
    return await food_crud.delete_food(db, original=food)