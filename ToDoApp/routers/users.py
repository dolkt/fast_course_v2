import sys
sys.path.append("..")

from fastapi import APIRouter, Depends, HTTPException, status
from database import engine, SessionLocal
from routers.auth import get_current_user, hash_password, get_user_exception
from sqlalchemy.orm import Session
from pydantic import BaseModel
import models

#class that will be the body of the post-request when user wants to update password.
class UpdatePassword(BaseModel):
    new_password: str


#Creates the database if it does not exist
models.Base.metadata.create_all(bind=engine)

#Setting up the router for this API.
router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={
        401: {"user": "Not authorized"},
        404: {"user": "Does not exist"}
    }
)

#Function to establish connection to database. To be used in instances where db needs to be called. Dependency injection.
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally: 
        db.close()

#Returning all the users in the database as json.
@router.get("/")
async def get_all_users(db: Session = Depends(get_db)):

    #Queries the table users and retrieves all. Like SELECT * from users;
    users = db.query(models.Users).all()

    #If query does not return anything (db is empty and not initialized) then exception will be raised.
    if not users:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No users found")

    return users

#Returns the user based on user id given in the path.
@router.get("/user/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):

    #Queries the table users given the user id. Like SELECT * FROM users WHERE user_id = <user_id>
    user = (
    db.query(models.Users)
    .filter(models.Users.user_id == user_id)
    .first()
    )

    #If user with user_id is not found in table then it will raise an 404 exception.
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No users found")

    return user

#Returns the users based on query parameters /user/?user_id=<user_id>
@router.get("/user/")
async def query_user(user_id: int, db: Session = Depends(get_db)):
    
    #Queries the table users given the user id. Like SELECT * FROM users WHERE user_id = <user_id>
    user = (
    db.query(models.Users)
    .filter(models.Users.user_id == user_id)
    .first()
    )

    #If user with user_id is not found in table then it will raise an 404 exception.
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No users found")

    return user

#Post request to change the password for the given authenticated user (with JWT).
@router.post("/change_password")
async def change_user_password(update_password: UpdatePassword, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    
    #If user could not be authenticated (non valid JWT) then user exception is thrown.
    if user is None:
        raise get_user_exception()

    #Queries the users table and returns the given, authenticated, user.
    current_user = (
        db.query(models.Users)
        .filter(models.Users.user_id == user.get("user_id"))
        .first()
    )

    #If query found the user it updates the user's password and encrypts it, given the provided password in the post body.
    if current_user:
        current_user.hashed_password = hash_password(update_password.new_password)
    
        #Adds the current user model in the db commit queue.
        db.add(current_user)

        #Commits the model within the queue.
        db.commit()

        return {"message": f"password updated for {user.get('username')}"}

    #If (for some reason) it could not be commited to database, an exception is thrown.
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not change password")

#Deletes the given authenticated user.
@router.delete("/user")
async def delete_user(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):

    #If the user is not authenticated via JWT then the user exception is thrown.
    if user is None:
        get_user_exception()
    
    #QUeries the table users for the given user_id (from decoded jwt-token)
    current_user = (
        db.query(models.Users)
        .filter(models.Users.user_id == user.get("user_id"))
        .delete()
    )

    #If user could not be found in db, then an exception is thrown.
    if not current_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    
    #Commits the deletion.
    db.commit()

    return {"message": f"user {user.get('username')} was deleted."}


