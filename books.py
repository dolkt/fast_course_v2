from fastapi import FastAPI, HTTPException, status
from enum import Enum
from typing import Union


book_app = FastAPI()


BOOKS = {
    "book_1": 
        {"title": "Title One", 
        "author": "Author One",
        },
    "book_2": 
        {"title": "Title Two", 
        "author": "Author Two",
        },
    "book_3": 
        {"title": "Title Three", 
        "author": "Author Three",
        },
    "book_4": 
        {"title": "Title Four", 
        "author": "Author Four",
        },
}


#Enumerations are possible in FastAPI
class DirectionName(str, Enum):
    north = "North"
    south = "South"
    west = "West"
    east = "East"

@book_app.get("/")
async def root():
    return {"message": "ET Phone Home"}


#Query parameter which is is optional (FastAPI knows since = None)
@book_app.get("/books")
async def get_some_books(skip_book: Union[str, None] = None):
    if skip_book:
        new_book_shelf = BOOKS.copy()
        del new_book_shelf[skip_book]
        return new_book_shelf
    return BOOKS

#Fetching using query params
@book_app.get("/assignment/")
async def get_book_query(book_id: str):
    return BOOKS[book_id.lower()]

@book_app.delete("/assignment/")
async def remove_book(book_id: str):
    for book in BOOKS:
        if book == book_id:
            del BOOKS[book_id]

            return {f"book with id {book_id} was removed"}
        
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with {book_id} not found")

#Fetching using Path params
@book_app.get("/books/{book_id}")
async def fetch_book_by_id(book_id: str):
    return BOOKS[book_id.lower()]


@book_app.post("/books/add_book")
async def add_book(book_title: str, book_author: str):
    retard_variable_to_show_the_highest_book_id = 0

    for book in BOOKS:
        current_book_id = int(book.split("_")[-1])
        if current_book_id > retard_variable_to_show_the_highest_book_id:
            retard_variable_to_show_the_highest_book_id = current_book_id
        
    BOOKS[f"book_{retard_variable_to_show_the_highest_book_id + 1}"] = {"title": book_title, "author": book_author}

    return {"mes": "yay"}



@book_app.get("/directions/{direction_name}")
def get_direction(direction_name: DirectionName):
    if direction_name == DirectionName.north:
        return {"Direction": direction_name, "go_to": "up!"}
    if direction_name == DirectionName.south:
        return {"Direction": direction_name, "go_to": "down!"}
    if direction_name == DirectionName.west:
        return {"Direction": direction_name, "go_to": "left!"}
    return  {"Direction": direction_name, "go_to": "right!"}
