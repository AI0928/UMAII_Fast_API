from pydantic import BaseModel

#Tokenのデータ型
class Token(BaseModel):
    access_token: str
    token_type: str