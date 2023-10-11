from fastapi import FastAPI

from api.routers import employee

app = FastAPI()

app.include_router(employee.router)