import sys
sys.path.append("..")

from fastapi import Depends, HTTPException, status, APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
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

#(Schema) The request body that can be sent to our API.
class Todo(BaseModel):
    title: str
    description: Union[str, None] = None
    priority: int = Field(ge=1, le=5, description="Priority must be between 1-5")
    complete: bool


class UpdateTodo(BaseModel):
    title: Union[str, None] = None
    description: Union[str, None] = None
    priority: Union[int, None] = Field(default=None, ge=1, le=5, description="Priority must be between 1-5")
    complete: Union[bool, None] = None

@router.get("/test")
async def test(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

#Parameter shows that the database session depends on the get_db function (It will run it so we have db connection)
@router.get("/")
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.ToDos).all() #Runs a query to the database table given in models.ToDos. The query is to return everything with .all().
    #Like saying SELECT * FROM todos


@router.get("/{todo_id}")
async def get_todo(todo_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Establishes connection to the database and tries to fetch todo given the id
    Relies on (Depends) establishing connection with the db, given by the get_db function
    
    ------
    Parameters
    todo_id - int of the todo id
    
    Returns
    The todo with the given todo id
    """
    if user is None:
        return get_user_exception()

    todo_model = (
        db.query(models.ToDos) #Queries the table given in models.ToDos
        .filter(models.ToDos.todo_id == todo_id)
        .filter(models.ToDos.user_id == user.get("user_id")) #Filters the query, kind of the WHERE clause in SQL (WHERE todo_id = id)
        .first() #Retrives the first hit in db. Like FIRST in SQL
    )

    if todo_model: #If it's found it returns the todo
        return todo_model
    
    raise http_exception_404(todo_id) #If it's not found it raises 404.

@router.get("/user")
async def read_all_by_user(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):

    if user is None:
        raise get_user_exception()
    
    return db.query(models.ToDos).filter(models.ToDos.owner_id == user.get("user_id")).all()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_todo(todo: Todo, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):

    if user is None:
        raise get_user_exception()
    
    todo_model = models.ToDos() #Instantiates the ToDo class from the models module. So we can call it's attributes which
    #are linked to a column in the database table

    #Below adds entries from the todo request body.
    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete
    todo_model.owner_id = user.get("user_id") #takes the user_id from the authenticated user. All above are from request body

    db.add(todo_model) #Adds the model in a queue to be added to the database.
    db.commit() #Flushes the queue above and adds it to database.

    return {
        "To Do added succesfully": todo
    }


@router.put("/{todo_id}")
async def update_todo(todo_id: int, todo: UpdateTodo, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):

    if user is None:
        raise get_user_exception()

    todo_model = (
        db.query(models.ToDos)
        .filter(models.ToDos.todo_id == todo_id)
        .filter(models.ToDos.owner_id == user.get("user_id"))
        .first()
    )

    if todo_model:
        if todo.title:
            todo_model.title = todo.title
        if todo.description:
            todo_model.description = todo.description
        if todo.priority:
            todo_model.priority = todo.priority
        if todo.complete:
            todo_model.complete = todo.complete

        db.add(todo_model)
        db.commit()
        
        return {"Message": f"To Do {todo_id} changed!"} if not todo.complete else {"Message": f"To Do {todo_id} complete!"}

    return http_exception_404(todo_id)

@router.delete("/{todo_id}")
async def delete_todo(todo_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):

    if user is None:
        raise get_user_exception()

    todo_model = (
        db.query(models.ToDos)
        .filter(models.ToDos.todo_id == todo_id)
        .filter(models.ToDos.owner_id == user.get("user_id"))
        .first()
    )

    if todo_model:
        db.query(models.ToDos).filter(models.ToDos.todo_id == todo_id).delete()
        db.commit()

        return {"Message": f"To Do {todo_id} was deleted"}
    
    return http_exception_404(todo_id)