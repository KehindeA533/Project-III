from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI, HTTPException, Path, status
from models import Todos
import models
from db import engine, SessionLocal

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# What is the purpose / need for this?
db_dependency = Annotated[Session, Depends(get_db)]


@app.get("/Todos", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(Todos).all()


@app.get("/Todos/{id}", status_code=status.HTTP_200_OK)
async def get_single_todos(db: db_dependency, id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, details="Todo not found."
    )
