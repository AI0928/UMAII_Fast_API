from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware # 追加

from api.routers import user as user_routers
from api.routers import food as food_routers
from api.routers import order as order_routers
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,   # 追加
    allow_methods=["*"],      # 追加
    allow_headers=["*"]       # 追加
)

app.include_router(user_routers.router)
app.include_router(food_routers.router)
app.include_router(order_routers.router)