import sys
sys.path.append("..")


from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import jwt, JWTError
from pydantic import BaseModel
from typing import Union
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models

#The secret key for encoding the jwt token request
SECRET_KEY = "TedSecretKey123"
#The algorithm used for encoding the jwt
ALGORITHM = "HS256"


#The post-request body for creating a user.
class CreateUser(BaseModel):
    username: str
    email: Union[str, None] = None
    first_name: str
    last_name: str
    password: str
    phone_num: str


#The hashfunction to be used for encrypting passwords
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#Creates the database if it does not exist
models.Base.metadata.create_all(bind=engine)

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")

#initializing the api - calling it auth_app
router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={401: {"user": "Not authorized"}}
)

#Function to establish connection to database. To be used in isntances where db needs to be called. Dependency injection.
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally: 
        db.close()


def hash_password(password: str) -> str:
    """
    Function to hash a password
    
    ------
    Parameters
    password: str of plain text password

    Returns
    Hashed password"""
    return bcrypt_context.hash(password)

def verify_password(plain_password, hashed_password) -> bool:
    """
    Checks if the plain text password validates towards the hashed password, using the encryption algorithm
    
    -----
    Parameters
    plain_pasword - str of plain text password
    hashsed_password - str of hashed password from bcrypt


    -----
    Returns
    Boolean - False or True depending on if the passwords matches decrypted.
    """
    return bcrypt_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str, db) -> dict:
    """
    Function to be used inside user authentication api methods
    
    If user is authenticated then it will return the user
    ------
    Parameters
    username: str of username in plain text
    password - str of password in plain text

    ------
    Returns
    """

    #queries the table users for the provided username 
    user = db.query(models.Users).filter(models.Users.username == username).first()

    #if username exists and the password is correct (validated towards the hashed password) the it returns the user in json
    if user and verify_password(plain_password=password, hashed_password=user.hashed_password):
        return user
    
    else:
        return False


def create_access_token(username: str, user_id: int, expires_delta: Union[timedelta, None] = None):
    """
    Creates jwt-token based on the encode dictionary with username and user_id.
    Lets the user have the option to set the expiry time (given in minutes) with expires_delta param.
    Encrypted with HS256 (from ALGORITHM)
    
    -------
    Parameters
    username: str of the username to create the token for
    user_id: int of the user_id to create the token for
    
    -------
    Returns
    jwt-token encoded with SH256 algorithm.
    """
    
    #Create the claims for the jwt-encoding. Will include "sub" key for username and "id" key for user_id 
    encode = {"sub": username, "id": user_id}

    #If expires_delta param is set then it will take current time (in utc) + timedelta in mins.
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    #includes in the claims when the token will expire.
    encode.update({"exp": expire})

    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_bearer)):
    """
    Decodes the jwt-token using the SECRET KEY and the given algorithm.
    Returns the username and user_id if the jwt can be decoded and the username exists.
    Depends on the ouath2 password form being filled out (eller???)    
    ------
    Parameters
    token: str of the decoded token"""

    #Decodes the encoded jwt in claims given the secret key and algorithm.
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        #Gets the username and user_id from the claims dictionary
        username: str = payload.get("sub")
        user_id: int = payload.get("id")

        #If username or user_id is not in the claims (from the jwt) then an user exception is thrown.
        if username is None or user_id is None:
            raise get_user_exception()
        
        return {"username": username, "user_id": user_id}
    
    #If JWT is incorrect then user exception is thrown.
    except JWTError:
        raise get_user_exception()

#Creates user in users table
@router.post("/user/create")
async def create_new_user(create_user: CreateUser, db: Session = Depends(get_db)):

    #model so we can assign values from the post request body to the db columns.
    create_user_model = models.Users()

    create_user_model.username = create_user.username
    create_user_model.email = create_user.email
    create_user_model.first_name = create_user.first_name
    create_user_model.last_name = create_user.last_name
    create_user_model.hashed_password = hash_password(create_user.password)
    create_user_model.is_active = True
    create_user_model.phone_number = create_user.phone_num

    #Adds the user model to the commit queue
    db.add(create_user_model)

    #Commits the things in the queue.
    db.commit()


@router.post("/token/")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    #Authenticates the user by checking form data from the api towards the username and password in the database.
    user = authenticate_user(form_data.username, form_data.password, db)

    #If user is not retrieved the it throws an token exception
    if not user:
        raise token_exception()

    #Sets the token expiry in 20mins
    token_expires = timedelta(minutes=20)

    #Creates an jwt token
    token = create_access_token(username=user.username, user_id=user.user_id, expires_delta=token_expires)

    return {"token":token}


#Exceptions
def get_user_exception():
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    return credentials_exception

def token_exception():
    token_exception_response = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"}
    )

    return token_exception_response