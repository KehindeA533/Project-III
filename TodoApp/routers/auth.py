from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException, Path, status
from pydantic import BaseModel, Field
from db import SessionLocal
from sqlalchemy.orm import Session
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt
import os
from dotenv import load_dotenv


"""
APIRouter instance for defining and grouping API routes.

This router can be used to organize and manage routes in a FastAPI application. Routes added to this router
can be mounted to the main application router with a specified prefix and set of tags.

This router is prefixed with "/auth" and includes all routes under the "auth" tag.

Attributes:
    prefix (str): The prefix for all routes defined in this router. All endpoints will start with "/auth".
    tags (list): A list of tags associated with the routes in this router. In this case, it is ["auth"].
"""
router = APIRouter(prefix="/auth", tags=["auth"])

"""
Initialize a CryptContext for bcrypt hashing.

This CryptContext is configured to use the bcrypt algorithm for hashing 
passwords. The `deprecated` parameter is set to "auto", which allows 
automatic handling of deprecated algorithms by the library.

Attributes:
    schemes (list): A list of hashing schemes to be supported by the context.
                    In this case, only "bcrypt" is included.
    deprecated (str): A string indicating how deprecated algorithms should
                      be handled. "auto" enables automatic management.

This can be used to hash and verify passwords securely using the bcrypt algorithm.
"""

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

load_dotenv()

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")


class UserRequest(BaseModel):
    email: str = Field(min_length=3)
    username: str
    first_name: str
    last_name: str
    password: str
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {"sub": username, "id": user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, user_request: UserRequest):
    user_model = Users(
        email=user_request.email,
        username=user_request.username,
        first_name=user_request.first_name,
        last_name=user_request.last_name,
        role=user_request.role,
        hashed_password=bcrypt_context.hash(user_request.password),
        is_active=True,
    )

    db.add(user_model)
    db.commit()


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        return "Fail Auth"
    token = create_access_token(user.username, user.id, timedelta(minutes=20))
    return {"access_token": token, "token_type": "bearer"}
