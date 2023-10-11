from typing import Optional

from pydantic import BaseModel, Field

class EmployeeBase(BaseModel):
    name: Optional[str] = Field(None, example="福沢諭吉")
    email: Optional[str] = Field(None, example="福沢諭吉")
    


class EmployeeCreate(EmployeeBase):
    password: Optional[str] = Field(None, example="pass")

class EmployeeCreateResponse(EmployeeCreate):
    id: int
    
    class Config:
        orm_mode = True

class Employee(EmployeeBase):
    id: int
    class Config:
        orm_mode = True