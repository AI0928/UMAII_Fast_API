from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from api.db import Base

#料理テーブル
class Food(Base):
    __tablename__ = "foods" #テーブル名

    id = Column(Integer, primary_key=True) #主キー
    name = Column(String(1024)) #名前