from fastapi import FastAPI

from api.routers import user as user_routers
from api.routers import food as food_routers
from api.routers import order as order_routers
app = FastAPI()

app.include_router(user_routers.router)
app.include_router(food_routers.router)
app.include_router(order_routers.router)