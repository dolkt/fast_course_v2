"""
Module for creating the database
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

#The url (directory) of the the database
#The DBMS, dbms:passowrd@host/db-name
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:z0lwT4nk123@localhost/ToDoApplicationDatabase"

#The "engine" that will drive the database. Here (as we set in the url) postgresql is driving the database.
engine = create_engine(url = SQLALCHEMY_DATABASE_URL)

#The session of the database - where autocommits (to database queue) and autoflush (flushing the queue to db) is not automatic.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#For setting up the base models of the tables with it's respective columns
Base = declarative_base()
