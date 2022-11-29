"""
Module for setting up the models of the application.
The classes below define the tables in the database
"""

from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


#Setting up the database tables
class Users(Base):
    #The table name
    __tablename__ = "users"

    #The table columns and it's definitions.
    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    phone_number = Column(String)
    #Setting up table connection where address.id is Primary Key and users.address_id is foreign key
    address_id = Column(Integer, ForeignKey("address.id"), nullable=True)

    #Setting up a connection between primary key here -> foreign key.
    todos = relationship("ToDos", back_populates="owner")
    address = relationship("Address", back_populates="user_address")

class ToDos(Base):
    #The table name
    __tablename__ = "todos"

    todo_id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.user_id"))

    #Connection between Users.user_id and ToDos.owner (foreign key)
    owner = relationship("Users", back_populates="todos")


class Address(Base):
    #The table name
    __tablename__ = "address"

    id = Column(Integer, primary_key=True, index=True)
    address1 = Column(String)
    address2 = Column(String)
    city = Column(String)
    state = Column(String)
    country = Column(String)
    postalcode = Column(String)
    apt_num = Column(String)

    user_address = relationship("Users", back_populates="address")
