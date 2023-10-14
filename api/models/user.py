from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from api.db import Base

#ユーザーテーブル作成
class User(Base):
    __tablename__ = "users" #テーブル名

    id = Column(Integer, primary_key=True) #主キー
    name = Column(String(1024)) #名前
    email = Column(String(256), unique=True) #email
    password = Column(String(256)) #パスワード