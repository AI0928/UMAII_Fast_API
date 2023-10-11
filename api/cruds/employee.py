from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from pymysql.constants import ER

import api.models.employee as employee_model
import api.schemas.employee as employee_schema
from typing import List, Tuple, Optional
from sqlalchemy import select
from sqlalchemy.engine import Result


################################################
async def get_user_by_email(
        db: AsyncSession,
        email: str
) -> employee_model.Employee or None:
    result = await db.execute(select(employee_model.Employee).where(employee_model.Employee.email == email))
    row = result.first()

    if row is not None:
        return row[0]
    else:
        return None

async def authorize_user(
        db: AsyncSession,
        email: str,
        password: str,
) -> employee_model.Employee or None:
    employee = await get_user_by_email(db, email)

    if employee is None:
        return None
    if not pwd_context.verify(password, employee.password):
        return None
    
    return employee
################################################




################################################
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

async def register_employee(
        db: AsyncSession,
        employee_create: employee_schema.EmployeeCreate
)  -> employee_model.Employee:
    
    try:
        employee = employee_model.Employee(**employee_create.dict())
        employee.password = pwd_context.hash(employee.password)

        db.add(employee)
        await db.commit()
        await db.refresh(employee)

        return employee
    except IntegrityError as e:
        db.rollback()
        raise e.orig
################################################
async def create_employee(
    db: AsyncSession, employee_create: employee_schema.EmployeeCreate
) -> employee_model.Employee:
    employee = employee_model.Employee(**employee_create.dict())
    db.add(employee)
    await db.commit()
    await db.refresh(employee)
    return employee

async def get_employees(db: AsyncSession) -> List[Tuple[int, str]]:
    result: Result = await (
        db.execute(
            select(
                employee_model.Employee.id,
                employee_model.Employee.name,
                employee_model.Employee.email,
                employee_model.Employee.password
            )
        )
    )
    return result.all()

async def get_employee(db: AsyncSession, employee_id: int) -> Optional[employee_model.Employee]:
    result: Result = await db.execute(
        select(employee_model.Employee).filter(employee_model.Employee.id == employee_id)
    )
    employee: Optional[Tuple[employee_model.Employee]] = result.first()
    return employee[0] if employee is not None else None  # 要素が一つであってもtupleで返却されるので１つ目の要素を取り出す


async def update_employee(
    db: AsyncSession, employee_create: employee_schema.EmployeeCreate, original: employee_model.Employee
) -> employee_model.Employee:
    original.name = employee_create.name
    original.email = employee_create.email
    original.password = employee_create.password
    db.add(original)
    await db.commit()
    await db.refresh(original)
    return original

async def delete_employee(db: AsyncSession, original: employee_model.Employee) -> None:
    await db.delete(original)
    await db.commit()