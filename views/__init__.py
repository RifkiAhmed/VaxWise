#!/usr/bin/python3
"""
This module initializes the Flask Blueprint for views used in the application.

"""
from flask import Blueprint

app_views = Blueprint('app_views', __name__)

from views.authentification import *
from views.child import *
from views.child_dose import *
from views.hospital import *
from views.index import *
from views.nurse import *
from views.user import *
from views.vaccine import *
