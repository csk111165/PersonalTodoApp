import sys
sys.path.append("..")  # since auth.py is now in router dir so database.py and models.py won't be accessible so this will
                       # so this will allow the parent dir of auth.py ie(router folder) to include all ohter dependency

from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, APIRouter, Request, Form
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from .auth import get_current_user
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from starlette.responses import RedirectResponse
from starlette import status


# app = FastAPI()
router = APIRouter(
    prefix="/todos",
    tags=["todos"],
    responses={404: {"description": "not found"}}
)

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

# This class is for providing the structure to post the result, it will show up when use want to post the result, they will have to pass
# these field to make sure they are not leaving anyting
class Todo(BaseModel):
    title: str
    description: Optional[str]
    priority: int = Field(gt=0, lt=6, description="The priority must be between 0 to 5")
    complete: bool


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get("/", response_class=HTMLResponse)
async def read_all_by_user(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    todos = db.query(models.Todos).filter(models.Todos.owner_id == user.get("id")).all()
    return templates.TemplateResponse("home.html", {"request": request, "todos": todos, "user": user})


@router.get("/add-todo", response_class=HTMLResponse)
async def add_new_todo(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("add-todo.html", {"request": request, "user": user})


@router.post("/add-todo", response_class=HTMLResponse)
async def create_todo(request: Request, title: str = Form(), description: str = Form(),
                priority: int = Form(), db: Session = Depends(get_db)
                ):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    todo_model = models.Todos()
    todo_model.title = title
    todo_model.description = description
    todo_model.priority = priority
    todo_model.complete = False
    todo_model.owner_id = user.get("id")

    db.add(todo_model)
    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

@router.get("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    return templates.TemplateResponse("edit-todo.html", {"request": request, "todo": todo, "user": user})



@router.post("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo_commit(request: Request, todo_id: int,  title: str = Form(), description: str = Form(),
                priority: int = Form(), db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if todo_model is None:  # this check is important when we delete any note it will be checked while rendring
        return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)
    todo_model.title = title
    todo_model.description = description
    todo_model.priority = priority

    db.add(todo_model)
    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


@router.get("/delete/{todo_id}", response_class=HTMLResponse)
async def delete_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).filter(models.Todos.owner_id == user.get("id")).first()
    if todo_model is not None:
        db.query(models.Todos).filter(models.Todos.id == todo_id).delete()
        db.commit()
        return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


@router.get("/complete/{todo_id}", response_class=HTMLResponse)
async def complete_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()

    todo.complete = not todo.complete

    db.add(todo)
    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)




# @router.get("/test")
# def test(request: Request):
#     return templates.TemplateResponse("register.html", {"request": request})

# @router.get("/")
# async def get_all_todos(db: Session = Depends(get_db)):
#     return db.query(models.Todos).all()


# @router.get("/user")
# def read_all_by_user(user: dict = Depends(get_current_user), db: Session = Depends(get_db)): # get_current_user is imported from the auth.py
#     if user is None:
#         raise HTTPException(status_code=404, detail="user is not found")
#     return db.query(models.Todos).filter(models.Todos.owner_id == user.get("id")).all()  # here user is {"sub" : cshekhar, "id": 1} , get() to retrive value from the dict
#                                                                                          # owner_id is the foreign key to map with the id of user
#                                                                                          # but first we need to generate the token and that token will be passed here

# # get todos by id


# @router.get("/{todo_id}")
# def get_todo_by_id(todo_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
#     if user is not None:
#         todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).filter(models.Todos.owner_id == user.get("id")).first()
#         if todo_model is not None:
#             return todo_model
#     raise http_exception()


# def http_exception():
#     return HTTPException(status_code=404, detail="Todo not found!")


# @router.post("/")
# async def create_todo(todo: Todo, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
#     # this is table
#     if user is not None:
#         todo_model = models.Todos()  # models.Todos is the class we have defined which represents our Todos table
#         todo_model.title = todo.title
#         todo_model.description = todo.description
#         todo_model.complete = todo.complete
#         todo_model.priority = todo.priority
#         todo_model.owner_id = user.get("id")
#         db.add(todo_model)
#         db.commit()

#         # this is just to show the user that it is posted now
#         return {
#             "status": 201,
#             'transaction': "Successful"
#         }
#     return {"invalid user"}


# # if we want to update the entry of todo by todo_id

# @router.put("/{todo_id}")
# async def update_todo(todo_id: int, todo: Todo, user: dict = Depends(get_current_user),  db: Session = Depends(get_db)):  # here todo: is the strcuture which user need to pass
#     if user is not None:
#         todo_model = db.query(models.Todos).filter(models.Todos.owner_id == user.get("id")).filter(models.Todos.id == todo_id).first()
#         # if we don't have that todo_id
#         if todo_model is None:
#             raise http_exception()

#         todo_model.title = todo.title
#         todo_model.description = todo.description
#         todo_model.priority = todo.priority
#         todo_model.complete = todo.complete

#         db.add(todo_model)
#         db.commit()

#         return {
#             "status": 20,
#             'transaction': "Updated the todos!!"
#         }
#     raise HTTPException(status_code=404, details="user is not authenticated")

# # if we want to delete a todo based on todo_id

# @router.delete("/{todo_id}")
# async def delete_todo(todo_id: int, user: dict = Depends(get_current_user),  db: Session = Depends(get_db)):
#     if user is not None:
#         todo_model = db.query(models.Todos).filter(models.Todos.owner_id == user.get("id")).filter(models.Todos.id == todo_id).first()

#         if todo_model is None:
#             raise http_exception()

#         # query , filter and then delete
#         db.query(models.Todos).filter(models.Todos.id == todo_id).delete()

#         db.commit()

#         return {
#             "status": 200,
#             'transaction': "Deleted the todo!!"
#         }

#     raise HTTPException(status_code=404, details="user is not authenticated")

