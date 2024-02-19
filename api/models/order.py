from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from api.db import Base

#注文テーブル
class Order(Base):
    __tablename__ = 'orders' #テーブル名

    id = Column(Integer, primary_key=True) #主キー
    food_id = Column(Integer) #料理のID
    user_id = Column(Integer) #ユーザーのID
    #datetime = Column(String(256)) #注文日時