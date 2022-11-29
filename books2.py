from fastapi import FastAPI, Query, HTTPException, status, Request, Form, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from enum import Enum
from typing import List, Union, Optional

book_api = FastAPI()

class Genre(str, Enum):
    drama = "Drama"
    action = "Action"
    romance = "Romance"
    sci_fi = "Sci-Fi"
    fantasy = "Fantasy"


class NegativeNumberException(Exception):
    def __init__(self, books_to_return):
        self.books_to_return = books_to_return


class Book(BaseModel):
    book_id: Union[UUID, None] = uuid4()
    title: str = Field(min_length=1)
    author: str = Field(min_length=1)
    genre: List[Genre]
    description: Optional[str] = Field(default=None,
                                        title="Description of the book",
                                        max_length=100)
    rating: Optional[int] = Field(default=None, 
                                ge=0,
                                le=100)

#Custom model that does not use rating
class BookNoRating(BaseModel):
    book_id: Union[UUID, None] = uuid4()
    title: str = Field(min_length=1)
    author: str = Field(min_length=1)
    genre: List[Genre]
    description: Optional[str] = Field(default=None,
                                        title="Description of the book",
                                        max_length=100)

class UpdateBook(BaseModel):
    book_id: Union[UUID, None] = Field(default=None)
    title: Union[str, None] = Field(default=None, min_length=1)
    author: Union[str, None] = Field(default=None, min_length=1)
    genre: Union[List[Genre], None]
    description: Union[str, None] = Field(default=None,
                                        title="Description of the book",
                                        max_length=100)
    rating: Union[int, None] = Field(default=None, 
                                ge=0,
                                le=100)


    class Config:
        schema_extra = {
            "example": {
                "id": "69f7287f-bcae-469c-a0d2-220bc25ad561",
                "title": "How to code",
                "author": "Not me",
                "genre": [
                    "Action",
                    "Fantasy"
                ],
                "description": "Very nice description",
                "rating": 89
            }
        }




BOOKS = [
    Book(
        title="Romantic Book",
        author="Some old single lady",
        genre=[
            "Romance",
            "Drama"
        ],
        description="Hopeless single lady finds dream husband",
        rating=69
    ),
    Book(
        title="Action Packed",
        author="Some fat dude",
        genre=[
            "Action"
        ],
        description="Machine guns everywhere",
        rating=71
    )
]

@book_api.exception_handler(NegativeNumberException)
async def negative_number_exception_handler(request: Request,
                                            exception: NegativeNumberException):
    return JSONResponse(
        status_code=418,
       content={"message": f"You are trying to fetch a negative number of books! {exception.books_to_return}"}
    )


@book_api.get("/books/")
def read_all_books(limit_books: Optional[int] = Query(default=0)):

    if limit_books == 0 or limit_books > len(BOOKS):
        return BOOKS

    if limit_books and limit_books < 0:
        raise NegativeNumberException(books_to_return=limit_books)
    
    return BOOKS[:limit_books]



@book_api.get("/books/search")
def fetch_book_by_id(book_id: UUID):
    for book in BOOKS:
        if book.book_id == book_id:
            return book
    
    raise item_not_found_exception(book_id)

#Using BookNoRating as response model
@book_api.get("/books/no_rating/search", response_model=BookNoRating)
def fetch_no_rating_book_by_id(book_id: UUID):
    for book in BOOKS:
        if book.book_id == book_id:
            return book
    
    raise item_not_found_exception(book_id)


#Adding custom HTTP response. 201 is better for post requests as it states something was created.
@book_api.post("/books/", status_code=status.HTTP_201_CREATED)
async def add_book(add_book: Book):
    BOOKS.append(add_book)

    return {"book_added": add_book}


#Using Forms - it will be form within the api that url encoded.
@book_api.post("/books/login")
async def books_login(username: str = Form(), password: str = Form()):
    return {"username": username, "password": password}

#Customer headers with Header
@book_api.get("/header")
async def read_header(random_header: Union[str, None] = Header(default=None)):
    return {"Random-Header": random_header}


#Assignment books 2
@book_api.get("/assignment")
async def fetch_book_auth(book_id: UUID, username: str = Header(), password: str = Header()):
    
    if (username != "FastAPIUser" or password != "test1234!"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid user")
    else:
        for book in BOOKS:
            if book.book_id == book_id:
                return book


@book_api.put("/books/")
async def update_book(updated_book: UpdateBook):
    for book in BOOKS:
        if book.book_id == updated_book.book_id:
            if updated_book.author:
                book.author = updated_book.author
            if updated_book.title:
                book.title = updated_book.title
            if updated_book.genre:
                book.genre = updated_book.genre
            if updated_book.description:
                book.description = updated_book.description
            if updated_book.rating:
                book.rating = updated_book.rating
            
            return {"message": "Book was updated"}
    raise item_not_found_exception(updated_book.book_id)


@book_api.delete("/books/{book_id}")
def delete_book(book_id: UUID):
    for book in BOOKS:
        if book.book_id == book_id:
            BOOKS.remove(book)

            return {"Deleted": book}
    raise item_not_found_exception(book_id)
        

    

def item_not_found_exception(book_id: UUID):
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail=f"Book with id {book_id} not in inventory",
        headers={"X-Header-Error": "Nothing with that UUID"}) 