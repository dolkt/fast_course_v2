import sys
sys.path.append("..")

from fastapi import Depends, HTTPException, status, APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette import status
from starlette.responses import RedirectResponse
from typing import Union
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from routers.auth import get_current_user, get_user_exception
import models

router = APIRouter(
    prefix="/todos",
    tags=["todos"],
    responses={404: {"description": "Not found"}}
)

models.Base.metadata.create_all(bind=engine)

#For directing the api to the html templates. This is the dir.
templates = Jinja2Templates(directory="templates")


#Exception handlers (DRY)
def http_exception_404(item_id: Union[str, int] = None):
    """
    Function that will return an "404 - item not found" if user is trying to fetch an object with an invalid id
    
    ------
    Parameters
    item_id: str | int of the item id in the database
    
    ------
    Returns
    HTTP Response 404 - Not found
    """

    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Your request: {item_id} not found!")

def get_db():
    """
    Establishes a connection with the database and sets the session.
    Closes the database when external functions relying on this function are done
    
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get("/", response_class=HTMLResponse)
async def read_all_by_user(request: Request, db: Session = Depends(get_db)):

    user_todos = db.query(models.ToDos).filter(models.ToDos.owner_id == 1).all()

    "Sends api request and returns the home with the layout given in home.html."


    return templates.TemplateResponse("home.html", {"request": request, "todos": user_todos})


@router.get("/add-todo", response_class=HTMLResponse)
async def add_new_todo(request: Request):
    return templates.TemplateResponse("add-todo.html", {"request": request})

@router.post("/add-todo", response_class=HTMLResponse)
async def create_todo(
    request: Request,
    title: str = Form(...), 
    description: str = Form(...),
    priority: int = Form(...),
    db: Session = Depends(get_db)):

    todo_model = models.ToDos()

    todo_model.title = title
    todo_model.description = description
    todo_model.priority = priority
    todo_model.complete = False
    todo_model.owner_id = 1

    db.add(todo_model)
    db.commit()

    #The return call redirects and calls a get request after the api-post method has been called
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

@router.get("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):

    todo = db.query(models.ToDos).filter(models.ToDos.todo_id == todo_id).first()

    return templates.TemplateResponse("edit-todo.html", {"request":request, "todo": todo})

@router.post("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo_commit(
    request: Request,
    todo_id: int,
    title: str = Form(...),
    description: str = Form(...),
    priority: int = Form(...),
    db: Session = Depends(get_db)):

    todo_model = db.query(models.ToDos).filter(models.ToDos.todo_id == todo_id).first()

    todo_model.title = title
    todo_model.description = description
    todo_model.priority = priority

    db.add(todo_model)
    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

#Since it is a fullstack application it will use http method get instead of post since we are calling the application
#And the delete function is handled within the edit-todo.html instead.
@router.get("/delete/{todo_id}")
async def delete_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):

    todo_model = db.query(models.ToDos).filter(models.ToDos.todo_id == todo_id).filter(models.ToDos.owner_id == 1).first()

    if todo_model is None:
        return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)
    
    db.query(models.ToDos).filter(models.ToDos.todo_id == todo_id).delete()

    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


@router.get("/complete/{todo_id}", response_class=HTMLResponse)
async def complete_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):

    todo = db.query(models.ToDos).filter(models.ToDos.todo_id == todo_id).first()

    #Will switch the complete bool (if currently False -> True and vice versa)
    todo.complete = not todo.complete 

    db.add(todo)
    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


    