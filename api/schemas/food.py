from typing import Optional

from pydantic import BaseModel, Field

#foodのデータ型
#共通のフィールド
class FoodBase(BaseModel):
    #Optional[]は値を指定するか、省略する場合は None を指定する
    #Field()はnameがNoneの場合はexampleを返す
    name: Optional[str] = Field(None, example="カレー")

#food作成時にリクエストボディとして受け取る型
class FoodCreate(FoodBase):
    #何も追加せずFoodBaseをそのまま使用する
    pass

#food作成時にレスポンスとして返す型
class FoodCreateResponse(FoodCreate):
    id: int

    #DBmodelからのデータを暗黙的に変換するための設定
    class Config:
        orm_mode = True

#food表示時に返す型
class Food(FoodBase):
    id: int

    #DBmodelからのデータを暗黙的に変換するための設定
    class Config:
        orm_mode = True
