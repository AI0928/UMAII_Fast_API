from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from api.db import Base

#データベース作成
#ユーザーテーブル
class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True)
    name = Column(String(1024))
    email = Column(String(256), unique=True)
    password = Column(String(256))