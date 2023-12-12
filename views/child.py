#!/bin/usr/python3
"""
This module handles views and routes for the Flask application, including git_child, delete_child, add_child,
update_child, and rendering templates for the application's user interface.

"""
from datetime import datetime
from flask import jsonify, request
from flask_login import current_user, login_required
import json
from models import storage
from models.tables import *
from modules.redirect_user import redirect_user
import uuid
from views import app_views


@app_views.route('/child/<id>', methods=['GET'])
@login_required
def get_child(id):
    """
    Retrieves a child's information by ID.

    Retrieves and returns information about a child by their unique ID. The function first checks
    if the child with the provided ID exists in the storage. If found, it returns the child's information
    in JSON format. If not found, an empty JSON response is returned.

    Arguments:
    - id: The unique identifier of the child whose information is to be retrieved.

    Returns:
    - JSON response containing the child's information if the child is found.
    - An empty JSON response if the child is not found.

    """
    child = storage.get_by_id(Child, id)
    if child:
        return jsonify(child.to_dict())
    return jsonify({})


@app_views.route('/child/<id>', methods=['DELETE'])
@login_required
def delete_child(id):
    """
    Deletes a child's information by ID.

    Deletes the information of a child identified by the provided ID. The function first ensures
    the user is redirected if they are not of type 'User'. Then, it attempts to retrieve the child
    with the given ID from the storage. If found, it deletes the child's information from the
    storage and saves the changes. It returns an empty JSON response regardless of the success
    or failure of the deletion process.

    Arguments:
    - id: The unique identifier of the child whose information is to be deleted.

    Returns:
    - An empty JSON response indicating the completion of the deletion process.

    """
    if redirect_user('User'):
        return redirect_user('User')
    child = storage.get_by_id(Child, id)
    if child:
        storage.delete(child)
        storage.save()
    return jsonify({})


@app_views.route('/child', methods=['POST'])
@login_required
def add_child():
    """
    Adds a new child to the system.

    Adds a new child to the system based on the provided data in the request. First, it ensures
    the user is redirected if they are not of type 'User'. Then, it extracts the necessary data
    from the request payload (first name, last name, birthday, and parent ID) and creates a new
    Child instance. This new child is then added to the storage and saved. The function returns
    an empty JSON response indicating the completion of the addition process.

    Returns:
    - An empty JSON response indicating the completion of the addition of a new child.

    """
    if redirect_user('User'):
        return redirect_user('User')
    data = json.loads(request.data)
    kwargs = {
        'id': str(uuid.uuid4()),
        'first_name': data['first_name'],
        'last_name': data['last_name'],
        'birthdate': datetime.strptime(data['birthdate'], '%Y-%m-%d'),
        'parent_id': current_user.id
    }
    new_child = Child(**kwargs)
    storage.new(new_child)
    storage.save()
    return jsonify({})


@app_views.route('/child', methods=['PUT'])
@login_required
def update_child():
    """
    Updates a child's information.

    Updates the information of an existing child in the system based on the provided data in the request.
    The function first ensures the user is redirected if they are not of type 'User'. Then, it extracts the
    necessary data from the request payload (child ID, first name, and birthday) and attempts to retrieve
    the corresponding child from the storage. If the child exists, it updates the specified attributes and
    saves the changes to the storage. The function returns an empty JSON response indicating the completion
    of the update process.

    Returns:
    - An empty JSON response indicating the completion of the update of a child's information.

    """
    if redirect_user('User'):
        return redirect_user('User')
    data = json.loads(request.data)
    kwargs = {
        'first_name': data['first_name'],
        'birthdate': datetime.strptime(data['birthdate'], '%Y-%m-%d'),
    }
    child = storage.get_by_id(Child, data['id'])
    if child:
        for key, value in kwargs.items():
            setattr(child, key, value)
        storage.save()
    return jsonify({})
