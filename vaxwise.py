#!/usr/bin/python3
"""
This module initializes and configures the Flask application for the VaxWise App.
It sets up routes, login manager, and connects to the database.
"""
from flask import Flask
from flask_login import LoginManager
from models import storage
from models.tables import Nurse, User
from modules.ordinal import ordinal
import os
from views import app_views


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.register_blueprint(app_views, url_prefix='/')
login_manager = LoginManager()
login_manager.login_view = 'app_views.login'
login_manager.init_app(app)
app.jinja_env.filters['ordinal'] = ordinal


@login_manager.user_loader
def load_user(user_id):
    """
    Loads the current user from the database.

    Args:
    - user_id: ID of the user

    Returns:
    - User or Nurse object based on the user ID

    """
    user = storage.get_by_id(User, user_id)
    if not user:
        user = storage.get_by_id(Nurse, user_id)
    return user


@app.teardown_appcontext
def teardown(_):
    """
    Closes the SQLAlchemy session after each request.

    This function is registered with Flask's app context teardown. It ensures the SQLAlchemy session
    is closed at the end of each request, preventing potential resource leaks and managing the
    lifecycle of the database connection.

    """
    storage.close()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
