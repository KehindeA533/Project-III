from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from ..db import Base
from ..main import app
from ..routers import get_current_user

SQLALCHEEMY_DATABASE_URL = "sqliite:///./testdb.db"

engine = create_engine(
    SQLALCHEEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poorclass=StaticPool,  #! ?
)

TestingSessionLocal = sessionmaker(autocommit=False, autoFlush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return {"username": "JohnDoe", "id": 1, "user_role": "admin"}


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user
