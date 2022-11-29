from fastapi import FastAPI
from database import engine
from routers import auth, todos, users, address
from starlette.staticfiles import StaticFiles
import models


#Setting up the main api relay.
todo_api = FastAPI()

#Creating the database and the respective tables if it does not exist.
models.Base.metadata.create_all(bind=engine)

#Adding static files to our application (sub-application) via application mounting

todo_api.mount("/static", StaticFiles(directory="static"), name="static")

#Routers for the different APIs
todo_api.include_router(auth.router)
todo_api.include_router(todos.router)
todo_api.include_router(users.router)
todo_api.include_router(address.router)
