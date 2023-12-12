#!/usr/bin/python3
"""Module handling database storage and interaction"""
from models.tables import *
from os import getenv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


class DBStorage:
    """Class managing database storage and interaction"""
    __engine = None
    __session = None

    def __init__(self):
        """
        Initialize the database engine.

        Retrieves environment variables for MySQL configuration and 
        creates a SQLAlchemy engine for database interaction.
        """
        MYSQL_USER = getenv('MYSQL_USER')
        MYSQL_PWD = getenv('MYSQL_PWD')
        MYSQL_HOST = getenv('MYSQL_HOST')
        MYSQL_DB = getenv('MYSQL_DB')
        self.__engine = create_engine('mysql+mysqldb://{}:{}@{}/{}'.
                                      format(MYSQL_USER,
                                             MYSQL_PWD,
                                             MYSQL_HOST,
                                             MYSQL_DB))

    def all(self, cls=None):
        """
        Get all objects from the session.

        Args:
        - cls: The class of objects to retrieve. If None, retrieves all objects.

        Returns:
        - A dictionary containing all objects, keyed by their class name and ID.
        """
        dictionary = {}
        objects = []
        if cls:
            objects = self.__session.query(cls).all()
        for obj in objects:
            key = "{}.{}".format(obj.__class__.__name__, obj.id)
            dictionary[key] = obj
        return dictionary

    def new(self, obj):
        """
        Add a new object to the session.

        Args:
        - obj: The object to be added to the session.
        """
        self.__session.add(obj)

    def save(self):
        """Commit changes made to the session to the database"""
        self.__session.commit()

    def delete(self, obj=None):
        """
        Delete an object from the session.

        Args:
        - obj: The object to be deleted from the session. If None, no action is taken.
        """
        if obj is not None:
            self.__session.delete(obj)

    def reload(self):
        """
        Configures database setup and initializes session for storage.

        This method configures the database setup by creating all tables defined in the Base 
        metadata using the provided engine (__engine). It initializes a session factory and 
        creates a scoped session to interact with the database (__session).

        Notes:
        - Creates database tables based on the metadata defined in Base.
        - Initializes a session factory and sets up a scoped session for database interaction.
        """
        Base.metadata.create_all(self.__engine)
        sess_factory = sessionmaker(bind=self.__engine, expire_on_commit=False)
        Session = scoped_session(sess_factory)
        self.__session = Session

    def get_by_id(self, cls, id):
        """
        Get an object by its ID.

        Args:
        - cls: The class of the object to retrieve.
        - id: The ID of the object.

        Returns:
        - The object retrieved by ID if found, else None.
        """
        key = "{}.{}".format(cls.__name__, id)
        return self.all(cls).get(key)
    
    def get_by_email(self, cls, email):
        """
        Get an object by its email attribute.

        Args:
        - cls: The class of the object to retrieve.
        - email: The email to match.

        Returns:
        - The object with the matching email if found, else None.
        """
        return self.__session.query(cls).filter_by(email=email).first()
    
    def get_by_token(self, cls, token):
        """
        Get an object by its token attribute.

        Args:
        - cls: The class of the object to retrieve.
        - token: The token to match.

        Returns:
        - The object with the matching token if found, else None.
        """
        return self.__session.query(cls).filter_by(token=token).first()
    
    def count(self, cls=None):
        """
        Count the number of objects in storage.

        Args:
        - cls: The class of objects to count. If None, counts all objects.

        Returns:
        - The count of objects.
        """
        return len(self.all(cls))
    
    def close(self):
        """Close the session"""
        self.__session.remove()
