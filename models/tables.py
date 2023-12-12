#!/bin/use/python3
"""Module defining database models for the vaccination reminder app."""
from flask_login import UserMixin
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()


class BaseModel():
    """Base model for database objects"""

    def to_dict(self):
        """Returns a dictionary containing all keys/values of the model."""
        # Exclude SQLAlchemy specific attribute
        exclude_attrs = ['_sa_instance_state']
        dic = {"__class__": self.__class__.__name__}
        for key, value in self.__dict__.items():
            if key not in exclude_attrs:
                dic[key] = value
        return dic


child_dose = Table('child_dose', Base.metadata,
                   Column('child_id', String(60),
                          ForeignKey('children.id'), primary_key=True),
                   Column('dose_id', String(60),
                          ForeignKey('doses.id'), primary_key=True))


child_dose_notifications = Table(
    'child_dose_notifications',
    Base.metadata,
    Column('child_id', String(60), ForeignKey('children.id')),
    Column('dose_id', String(60), ForeignKey('doses.id')))


class Hospital_Vaccine(Base):
    """Model representing the link between hospitals and vaccines."""
    __tablename__ = 'hospital_vaccine'
    id = Column(String(60), primary_key=True)
    quantity = Column(Integer, default=0)
    hospital_id = Column(String(60), ForeignKey('hospitals.id'))
    vaccine_id = Column(String(60), ForeignKey('vaccines.id'))


class Dose(BaseModel, Base):
    """Model representing vaccination doses."""
    __tablename__ = 'doses'
    id = Column(String(60), primary_key=True, default=str(uuid.uuid4()))
    denomination = Column(String(128), unique=True)
    term = Column(Integer)
    vaccine_id = Column(String(60), ForeignKey('vaccines.id'))


class Vaccine(BaseModel, Base):
    """Model representing vaccines."""
    __tablename__ = 'vaccines'
    id = Column(String(60), primary_key=True, default=str(uuid.uuid4()))
    denomination = Column(String(128), unique=True)
    description = Column(String(1024))
    stock = Column(Integer)
    doses = relationship('Dose', backref="vaccine",
                         cascade="all, delete, delete-orphan")
    hospitals = relationship('Hospital_Vaccine', backref="vaccine",
                             cascade="all, delete, delete-orphan")


class Child(BaseModel, Base):
    """Model representing children."""
    __tablename__ = 'children'
    id = Column(String(60), primary_key=True, default=str(uuid.uuid4()))
    first_name = Column(String(128))
    last_name = Column(String(128))
    birthdate = Column(DateTime)
    parent_id = Column(String(60), ForeignKey('users.id'))
    doses = relationship('Dose', secondary=child_dose, backref='child')
    doses_notified = relationship('Dose', secondary=child_dose_notifications,
                                  backref='notified_child')


class User(BaseModel, Base, UserMixin):
    """Model representing users."""
    __tablename__ = 'users'
    id = Column(String(60), primary_key=True, default=str(uuid.uuid4()))
    email = Column(String(128), unique=True)
    password = Column(String(128))
    first_name = Column(String(128))
    last_name = Column(String(128))
    status = Column(String(32))
    token = Column(String(128))
    children = relationship('Child', backref="parent",
                            cascade="all, delete, delete-orphan")


class Nurse(BaseModel, Base, UserMixin):
    """Model representing nurses."""
    __tablename__ = 'nurses'
    id = Column(String(60), primary_key=True, default=str(uuid.uuid4()))
    email = Column(String(128), unique=True)
    password = Column(String(128))
    first_name = Column(String(128))
    last_name = Column(String(128))
    status = Column(String(32))
    token = Column(String(128))
    hospital_id = Column(String(60), ForeignKey('hospitals.id'))


class Hospital(BaseModel, Base):
    """Model representing hospitals."""
    __tablename__ = 'hospitals'
    id = Column(String(60), primary_key=True, default=str(uuid.uuid4()))
    name = Column(String(128))
    nurses = relationship('Nurse', backref='hospital')
    vaccines = relationship('Hospital_Vaccine',
                            backref="hospital",
                            cascade="all, delete, delete-orphan")
