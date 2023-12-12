#!/usr/bin/python3
"""
This module handles views and routes for the Flask application, including get_user, update_user,
parent_children and rendering templates for the application's user interface.

"""
from flask import jsonify, request
from flask_login import current_user, login_required, logout_user
import json
from models import storage
from models.tables import *
from modules.redirect_user import redirect_user
from views import app_views
from werkzeug.security import generate_password_hash


@app_views.route('/<email>', methods=['GET'])
@login_required
def get_user(email):
    """
    Retrieves user information based on the provided email.

    Retrieves user information based on the provided email address in the URL parameter.
    The function ensures that only authenticated users can access this endpoint.
    It searches for both regular users and nurses using the provided email.
    If a user or nurse with the provided email exists, it returns a JSON response indicating their existence.
    Otherwise, it returns a JSON response indicating the non-existence of a user or nurse with the given email.

    Args:
    - email: Email address used to search for user or nurse information.

    Returns:
    - A JSON response indicating the existence or non-existence of a user or nurse with the provided email.

    """
    user = storage.get_by_email(User, email)
    nurse = storage.get_by_email(Nurse, email)
    if user or nurse:
        return jsonify({"status": "Exist"})
    return jsonify({"status": "Not Exist"})


@app_views.route('/user', methods=['PUT'])
@login_required
def update_user():
    """
    Updates user information.

    Updates the current logged-in user's information based on the provided data in the request.
    The function ensures that only authenticated users of type 'User' can access this functionality.
    It retrieves the current user's information and updates it with the provided data.
    Passwords are hashed before being stored. If the update involves an email change, the user's status
    is set to 'unverified', triggering an email verification process.
    After updating the user information, the changes are saved, and based on the user's status, 
    it either triggers an email verification, logs the user out, and redirects them to the verification page,
    or returns an empty JSON response indicating successful update without any additional action.

    Returns:
    - An empty JSON response upon successful update of user information.
    - A JSON response containing a redirection link if the user's email needs verification.

    """
    from views.authentification import verify_email
    if redirect_user('User'):
        return redirect_user('User')
    data = json.loads(request.data)
    user = storage.get_by_id(User, current_user.id)
    data['password'] = generate_password_hash(data['password'],
                                              method='pbkdf2:sha256')
    if 'email' in data:
        data['status'] = 'unverified'
    for key, value in data.items():
        setattr(user, key, value)
    storage.save()
    if user.status != 'verified':
        verify_email(user)
        logout_user()
        return jsonify({'href': '/verification'})
    return jsonify({'href': ''})


@app_views.route('/user/children', methods=['POST'])
@login_required
def parent_children():
    """
    Retrieves children associated with a parent user.

    Retrieves children associated with a parent user based on the provided email in the request data.
    The function ensures that only users who are of type 'Nurse' can access this functionality.
    It fetches the user using the given email and retrieves information about their children, returning
    a JSON response containing the children's details if the user is found.

    Returns:
    - A JSON response containing the details of children associated with the parent user (if found).

    """
    if redirect_user('Nurse'):
        return redirect_user('Nurse')
    data = json.loads(request.data)
    user = storage.get_by_email(User, data.get('email'))
    if user:
        children = [child.to_dict() for child in user.children]
        return jsonify(children)
    return jsonify({})