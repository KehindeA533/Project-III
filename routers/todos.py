# import sys
# sys.path.append('..')

# import models
from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, HTTPException, Path, status, Request
from models import Todos
from db import SessionLocal
from .auth import get_current_user
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(
    # prefix="/todos",
    # tags=['todos'],
    # responses={404: {"description": "Not found"}}
)

# models.Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6, description="The prority must be between 1 - 5")
    complete: bool


@router.get("/test")
async def test(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@router.get("/Todos", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    return db.query(Todos).filter(Todos.owner_id == user.get("id")).all()


@router.get("/Todos/{id}", status_code=status.HTTP_200_OK)
async def get_single_todos(
    user: user_dependency, db: db_dependency, id: int = Path(gt=0)
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    todo_model = (
        db.query(Todos)
        .filter(Todos.id == id)
        .filter(Todos.owner_id == user.get("id"))
        .first()
    )
    if todo_model is not None:
        return todo_model
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, details="Todo not found."
    )


@router.post("/Todos", status_code=status.HTTP_201_CREATED)
async def create_todo(
    user: user_dependency, db: db_dependency, todo_request: TodoRequest
):
    """_summary_

    This line of code takes a TodoRequest object, converts it into a dictionary using model_dump(),
    and then uses that dictionary to create a new instance of the Todos class.
    It essentially transforms a request for a todo item into a database entry
    """
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )
    todo_model = Todos(**todo_request.model_dump(), owner_id=user.get("id"))
    db.add(todo_model)
    db.commit()


@router.put("/Todos/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
    db: db_dependency, todo_request: TodoRequest, id: int = Path(gt=0)
):
    todo_model = db.query(Todos).filter(Todos.id == id).first()

    if todo_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, details="Todo not found."
        )

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()


@router.delete("/Todos/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == id).first()

    if todo_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, details="Todo not found."
        )

    # db.query(Todos).filter(Todos.id == id).delete()
    db.delete(todo_model)
    db.commit()
