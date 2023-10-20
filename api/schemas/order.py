from typing import Optional

from pydantic import BaseModel, Field

#orderのデータ型
#共通のフィールド
class OrderBase(BaseModel):
    #Optional[]は値を指定するか、省略する場合は None を指定する
    #Field()はnameがNoneの場合はexampleを返す
    user_id: Optional[int] = Field(None, example=1)
    food_id: Optional[int] = Field(None, example=1)

#food作成時にリクエストボディとして受け取る型
class OrderCreate(OrderBase):
    #何も追加せずFoodBaseをそのまま使用する
    pass

#food作成時にレスポンスとして返す型
class OrderCreateResponse(OrderCreate):
    id: int

    #DBmodelからのデータを暗黙的に変換するための設定
    class Config:
        orm_mode = True

#food表示時に返す型
class Order(OrderBase):
    id: int

    #DBmodelからのデータを暗黙的に変換するための設定
    class Config:
        orm_mode = True