from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from typing import Annotated
from pymysql.err import IntegrityError
from pymysql.constants import ER

from datetime import datetime, timedelta

import api.schemas.employee as employee_schema
import api.cruds.employee as employee_crud
from api.schemas import token as token_schema
from api.models import employee as employee_model
from api.db import get_db
from api.settings import get_settings, Settings

from jose import jwt, JWTError

ACCESS_TOKEN_EXPIRE_MINUTES = 30

ALGORITHM = 'HS256'
SECRET_KEY ='secret'

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/token')
oauth2_scheme_noerr = OAuth2PasswordBearer(tokenUrl='/api/token', auto_error=False)

router = APIRouter()

##############################################
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

    user = await employee_crud.get_user_by_email(db, email)

    return user


@router.get('/api/is_logined')
async def is_logined(employee: Annotated[employee_model.Employee or None, Depends(get_user_if_exists)]):
    return { 'is_logined': employee is not None }
##############################################




##############################################
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

    user = await employee_crud.get_user_by_email(db, email)
    if user is None:
        raise credentials_exception

    return user

@router.get('/api/user/me', response_model=employee_schema.Employee)
async def get_user_me(user: Annotated[employee_model.Employee, Depends(get_user)]):
    return user
##############################################




##############################################
def create_access_token(data: dict, expires_delta: timedelta, secret_key: str):
    expire = datetime.utcnow() + expires_delta
    return jwt.encode({ **data, 'exp': expire }, secret_key, algorithm=ALGORITHM)
##############################################



##############################################
@router.post('/api/token', response_model=token_schema.Token)
async def login(
    form:  Annotated[OAuth2PasswordRequestForm, Depends()], 
    db: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[str, Depends(get_settings)]
):
    employee = await employee_crud.authorize_user(db, form.username, form.password)
    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='incorrect email or password'
        )
    token = create_access_token(
        { 'sub': employee.email },
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        secret_key=settings.secret_key
    )
    return token_schema.Token(access_token=token, token_type='bearer')
##############################################



###############################################
@router.post('/api/register', response_model=employee_schema.Employee)
async def register(employee_create: employee_schema.EmployeeCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        employee = await employee_crud.register_employee(db, employee_create)
        return employee
    except IntegrityError as e:
        errcode, _ = e.args
        if errcode == ER.DUP_ENTRY:
            raise HTTPException(
                status_code = status.HTTP_409_CONFLICT,
                detail='already used email address'
            )
        else:
            raise
###############################################

###############################################
# @router.post('/api/token', response_model=token_schema.Token)
# async def login(form: Annotated[OAuth2PasswordRequestForm, Depends()]):
#     pass
###############################################

@router.get("/employees", response_model=List[employee_schema.Employee])
async def list_employees(db: AsyncSession = Depends(get_db)):
    return await employee_crud.get_employees(db)


@router.post("/employees", response_model=employee_schema.EmployeeCreateResponse)
async def create_employee(employee_body: employee_schema.EmployeeCreate, db: AsyncSession = Depends(get_db)):
    return await employee_crud.create_employee(db, employee_body)


@router.put("/employees/{employee_id}", response_model=employee_schema.EmployeeCreateResponse)
async def update_employee(employee_id: int, employee_body: employee_schema.EmployeeCreate, db: AsyncSession = Depends(get_db)):
    employee = await employee_crud.get_employee(db, employee_id=employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    return await employee_crud.update_employee(db, employee_body, original=employee)


@router.delete("/employees/{employee_id}", response_model=None)
async def delete_employee(employee_id: int, db: AsyncSession = Depends(get_db)):
    employee = await employee_crud.get_employee(db, employee_id=employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    return await employee_crud.delete_employee(db, original=employee)