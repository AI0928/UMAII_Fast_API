from sqlalchemy import create_engine

from api.models.user import Base
from api.models.food import Base
from api.models.order import Base

DB_URL = "mysql+pymysql://root@db:3306/demo?charset=utf8"
engine = create_engine(DB_URL, echo=True)

def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    reset_database()

#$ docker-compose exec app poetry run python -m api.migrate_db
#$ docker-compose exec db mysql demo
