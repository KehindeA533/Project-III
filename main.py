from fastapi import FastAPI
import models
from db import engine
from routers import auth, todos
from starlette.staticfiles import StaticFiles

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/healthy")
def health_check():
    return {"status": "Healthy"}


app.include_router(auth.router)
app.include_router(todos.router)
# app.include_router(admin.router)
# app.include_router(users.router)
