from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from typing import Annotated
from pymysql.err import IntegrityError
from pymysql.constants import ER

from datetime import datetime, timedelta

import api.schemas.user as user_schema
import api.cruds.user as user_crud
from api.schemas import token as token_schema
from api.models import user as user_model
from api.db import get_db
from api.settings import get_settings, Settings

from jose import jwt, JWTError

#ログインしたときのトークンの制限時間？
ACCESS_TOKEN_EXPIRE_MINUTES = 30

#パスワードのハッシュ化の設定？
ALGORITHM = 'HS256'
SECRET_KEY ='secret'

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/token') #リクエストヘッダからトークンを受け取る処理
oauth2_scheme_noerr = OAuth2PasswordBearer(tokenUrl='/api/token', auto_error=False) #リクエストヘッダからトークンを受け取る処理,トークンがない場合はNoneを返す

router = APIRouter()


#ユーザーがログインしているか判定する関数
#
async def get_user_if_exists(
        token: Annotated[str, Depends(oauth2_scheme_noerr)],
        db: Annotated[AsyncSession, Depends(get_db)],
        settings: Annotated[Settings, Depends(get_settings)],
):
    if token is None:
        return token

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        email = payload.get('sub')
    except JWTError:
        return None

    user = await user_crud.get_user_by_email(db, email)

    return user

#ユーザーがログインいているかを確認するAPI
#ログインしていたらTrue
#ログインしていなかったらNone(たぶん)
@router.get('/api/is_logined')
async def is_logined(user: Annotated[user_model.User or None, Depends(get_user_if_exists)]):
    return { 'is_logined': user is not None }

#ログインしているユーザーの情報を返す関数
async def get_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        db: Annotated[AsyncSession, Depends(get_db)],
        settings: Annotated[Settings, Depends(get_settings)],
):
    credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        email = payload.get('sub')
    except JWTError:
        raise credentials_exception

    user = await user_crud.get_user_by_email(db, email)
    if user is None:
        raise credentials_exception

    return user

#ログインしているユーザーの情報を返すAPI
@router.get('/api/user/me', response_model=user_schema.User)
async def get_user_me(user: Annotated[user_model.User, Depends(get_user)]):
    return user

#ログインに成功したらアクセストークンを返す関数
def create_access_token(data: dict, expires_delta: timedelta, secret_key: str):
    expire = datetime.utcnow() + expires_delta
    return jwt.encode({ **data, 'exp': expire }, secret_key, algorithm=ALGORITHM)

#ログイン用のAPI
#ログインに成功したらアクセストークンを返す
@router.post('/api/token', response_model=token_schema.Token)
async def login(
    form:  Annotated[OAuth2PasswordRequestForm, Depends()], 
    db: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[str, Depends(get_settings)]
):
    user = await user_crud.authorize_user(db, form.username, form.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='incorrect email or password'
        )
    token = create_access_token(
        { 'sub': user.email },
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        secret_key=settings.secret_key
    )
    return token_schema.Token(access_token=token, token_type='bearer')

#ユーザー登録用のAPI
@router.post('/api/register', response_model=user_schema.User)
async def register(user_create: user_schema.UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        user = await user_crud.register_user(db, user_create)
        return user
    except IntegrityError as e:
        errcode, _ = e.args
        if errcode == ER.DUP_ENTRY:
            raise HTTPException(
                status_code = status.HTTP_409_CONFLICT,
                detail='already used email address'
            )
        else:
            raise

#ユーザー全員の情報を返すAPI
@router.get("/users", response_model=List[user_schema.User])
async def list_users(db: AsyncSession = Depends(get_db)):
    return await user_crud.get_users(db)

#使わない
# @router.post("/users", response_model=user_schema.UserCreateResponse)
# async def create_user(user_body: user_schema.UserCreate, db: AsyncSession = Depends(get_db)):
#     return await user_crud.create_user(db, user_body)

#ユーザー情報の更新
@router.put("/users/{user_id}", response_model=user_schema.UserCreateResponse)
async def update_user(user_id: int, user_body: user_schema.UserCreate, db: AsyncSession = Depends(get_db)):
    user = await user_crud.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    return await user_crud.update_employee(db, user_body, original=user)


#ユーザー情報の削除
@router.delete("/users/{user_id}", response_model=None)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await user_crud.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    return await user_crud.delete_user(db, original=user)