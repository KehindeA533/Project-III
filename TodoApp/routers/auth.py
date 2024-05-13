from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from db import SessionLocal
from sqlalchemy.orm import Session
from models import Users

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class UserRequest(BaseModel):
    email: str = Field(min_length=3)
    username: str
    first_name: str
    last_name: str
    password: str
    role: str


@router.post("/auth")
async def create_user(db: db_dependency, user_request: UserRequest):
    # user_model = Users(**user_request.model_dump())
    user_model = Users(
        email=user_request.email,
        username=user_request.username,
        first_name=user_request.first_name,
        last_name=user_request.last_name,
        role=user_request.role,
        hashed_password=user_request.password,
        is_active=True,
    )

    return user_model

    # db.add(user_model)
    # db.commit()
