from fastapi import FastAPI, Depends, HTTPException
import models
from database import engine, SessionLocal
from routers import auth, todos
from starlette.staticfiles import StaticFiles
from starlette import status
from starlette.responses import RedirectResponse


app = FastAPI()

models.Base.metadata.create_all(bind=engine)

# include the static folder which will contain css and js

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return RedirectResponse("/todos", status_code=status.HTTP_302_FOUND)


app.include_router(auth.router)
app.include_router(todos.router)

