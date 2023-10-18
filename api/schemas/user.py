from typing import Optional

from pydantic import BaseModel, Field

#ユーザーのデータ型
#UserBaseはユーザーに関するすべての処理で扱う型
class UserBase(BaseModel):
    #Optional[]は値を指定するか、省略する場合は None を指定する
    #Field()はnameがNoneの場合はexampleを返す
    name: Optional[str] = Field(None, example="福沢諭吉")
    email: Optional[str] = Field(None, example="yukichi@example.com")
    
#UserBaseにpasswordを加えた型
#ユーザー作成時にリクエストボディとして受け取る型
class UserCreate(UserBase):
    password: Optional[str] = Field(None, example="pass")

#UserCreateにidを加えた型
#ユーザー作成時にレスポンスとして返す型
class UserCreateResponse(UserCreate):
    id: int
    
    #DBmodelからのデータを暗黙的に変換するための設定
    class Config:
        orm_mode = True

#UserCreateにidを加えた型
#ユーザー表示時に返す型
class User(UserBase):
    id: int
    class Config:
        orm_mode = True