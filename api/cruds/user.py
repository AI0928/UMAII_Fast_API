from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from pymysql.constants import ER

import api.models.user as user_model
import api.schemas.user as user_schema
from typing import List, Tuple, Optional
from sqlalchemy import select
from sqlalchemy.engine import Result


#emailからユーザーを特定する関数
async def get_user_by_email(
        db: AsyncSession,
        email: str
) -> user_model.User or None:
    #
    result = await db.execute(select(user_model.User).where(user_model.User.email == email))
    row = result.first()

    if row is not None:
        return row[0]
    else:
        return None

#パスワードが一致するかの関数
async def authorize_user(
        db: AsyncSession,
        email: str,
        password: str,
) -> user_model.User or None:
    user = await get_user_by_email(db, email)

    if user is None:
        return None
    if not pwd_context.verify(password, user.password):
        return None
    
    return user



pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
#パスワードをハッシュ化して登録する
async def register_user(
        db: AsyncSession,
        user_create: user_schema.UserCreate
)  -> user_model.User:
    
    try:
        user = user_model.User(**user_create.dict())
        user.password = pwd_context.hash(user.password)

        db.add(user)
        await db.commit()
        await db.refresh(user)

        return user
    except IntegrityError as e:
        db.rollback()
        raise e.orig
################################################

#使わない
async def create_user(
    db: AsyncSession, user_create: user_schema.UserCreate
) -> user_model.User:
    user = user_model.User(**user_create.dict())
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

#全てのユーザーを返す関数
async def get_users(db: AsyncSession) -> List[Tuple[int, str, str]]:
    result: Result = await (
        db.execute(
            select(
                user_model.User.id,
                user_model.User.name,
                user_model.User.email
            )
        )
    )
    return result.all()

#任意のユーザーを返す関数
async def get_user(db: AsyncSession, user_id: int) -> Optional[user_model.User]:
    result: Result = await db.execute(
        select(user_model.User).filter(user_model.User.id == user_id)
    )
    user: Optional[Tuple[user_model.User]] = result.first()
    return user[0] if user is not None else None  # 要素が一つであってもtupleで返却されるので１つ目の要素を取り出す

#ユーザーの情報を更新する関数
#パスワードがハッシュかされないため注意
async def update_user(
    db: AsyncSession, user_create: user_schema.UserCreate, original: user_model.User
) -> user_model.User:
    original.name = user_create.name
    original.email = user_create.email
    original.password = user_create.password
    db.add(original) #データを追加
    await db.commit() #変更を更新
    await db.refresh(original)
    return original

#任意のユーザーを削除する関数
async def delete_user(db: AsyncSession, original: user_model.User) -> None:
    await db.delete(original) #DBから削除
    await db.commit() #変更を保存