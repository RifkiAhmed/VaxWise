#!/usr/bin/python3
"""
Initialize the database storage for models.

This script initializes the database storage by creating an instance of the 'DBStorage' class 
from the 'db_storage' module. It instantiates a 'storage' object and invokes the 'reload()' 
method to configure the database storage for the models.
"""

from models.db_storage import DBStorage
storage = DBStorage()
storage.reload()