#!/usr/bin/python3
"""
This module handles views and routes for the Flask application, including, get_hospital, get_hospitals, add_hospital, 
hospital_nurses, hospital_vaccines, hospital_add_vaccine and rendering templates for the application's user interface.

"""
from flask import jsonify, render_template, request
from flask_login import current_user, login_required
import json
from models import storage
from models.tables import *
from modules.redirect_user import redirect_user
import uuid
from views import app_views


@app_views.route('/hospital/<name>', methods=['GET'])
@login_required
def get_hospital(name):
    """
    Retrieves a hospital by name.

    Retrieves and checks if a hospital exists in the system based on the provided name.
    The function ensures the user is redirected if they are not of type 'Admin'. It fetches
    all hospitals from the storage and extracts their names to create a list of lowercase
    hospital names. It then checks if the provided name (converted to lowercase) exists
    within this list of hospital names. If found, it returns a JSON response with status
    'Exist'; otherwise, it returns a JSON response with status 'Not Exist'.

    Arguments:
    - name: The name of the hospital to be retrieved and checked.

    Returns:
    - JSON response: {'status': 'Exist'} if the hospital exists.
    - JSON response: {'status': 'Not Exist'} if the hospital does not exist.

    """
    if redirect_user('Admin'):
        return redirect_user('Admin')
    hospitals = storage.all(Hospital).values()
    hospital_names = [hospital.name.lower() for hospital in hospitals]
    if name.lower() in hospital_names:
        return jsonify({ 'status': 'Exist'})
    return jsonify({ 'status': 'Not Exist'})


@app_views.route('/hospitals', methods=['GET'])
@login_required
def get_hospitals():
    """
    Renders a list of hospitals.

    Renders the 'admin-2.html' template displaying a list of hospitals available in the system.
    The function ensures the user is redirected if they are not of type 'Admin'. It retrieves all
    hospitals from the storage, sorts them alphabetically by name, and sends the sorted list to
    the 'admin-2.html' template for rendering.

    Returns:
    - Renders the 'admin-2.html' template with the sorted list of hospitals and the current user's
      information for display.

    """
    if redirect_user('Admin'):
        return redirect_user('Admin')
    hospitals = storage.all(Hospital).values()
    sorted_hospitals = sorted(hospitals, key=lambda hospital: hospital.name)
    return render_template("admin-2.html", hospitals=sorted_hospitals,
                           user=current_user)


@app_views.route('/hospital', methods=['POST'])
@login_required
def add_hospital():
    """
    Adds a new hospital to the system.

    Adds a new hospital to the system based on the provided data in the request. The function ensures
    the user is redirected if they are not of type 'Admin'. It extracts the necessary data from the request
    payload (hospital name) and creates a new Hospital instance. This new hospital is then added to the
    storage, and for each existing vaccine in the system, a record is created in the Hospital_Vaccine
    table to initialize the hospital's inventory of vaccines. The function returns an empty JSON response
    indicating the completion of the addition process.

    Returns:
    - An empty JSON response indicating the completion of adding a new hospital.

    """
    if redirect_user('Admin'):
        return redirect_user('Admin')
    data = json.loads(request.data)
    kwargs = {
        'id': str(uuid.uuid4()),
        'name': data['name']
    }
    hospital = Hospital(**kwargs)
    storage.new(hospital)
    storage.save()
    vaccines = storage.all(Vaccine).values()
    for vaccine in vaccines:
        new_hospital_vaccine = Hospital_Vaccine(id=str(uuid.uuid4()),
                                                hospital_id=hospital.id,
                                                vaccine_id=vaccine.id)
        storage.new(new_hospital_vaccine)
        storage.save()
    return jsonify({})


@app_views.route('/hospital/nurses', methods=['POST'])
@login_required
def hospital_nurses():
    """
    Retrieves nurses associated with a hospital.

    Retrieves and returns a list of nurses associated with a specific hospital based on the provided
    hospital ID in the request. The function ensures the user is redirected if they are not of type 'Admin'.
    It fetches all nurses from the storage and creates a list containing details of nurses linked to
    the given hospital ID. This list is then returned in JSON format.

    Returns:
    - JSON response: A list of nurse details associated with the specified hospital ID.

    """
    if redirect_user('Admin'):
        return redirect_user('Admin')
    data = json.loads(request.data)
    nurses = storage.all(Nurse).values()
    nurses_list = []
    for nurse in nurses:
        if nurse.hospital_id == data['id']:
            nurses_list.append(nurse.to_dict())
    return jsonify(nurses_list)


@app_views.route('/hospital/vaccines', methods=['POST'])
@login_required
def hospital_vaccines():
    """
    Retrieves vaccines available in a hospital.

    Retrieves and returns a list of vaccines available in a specific hospital based on the provided
    hospital ID in the request. The function ensures the user is redirected if they are not of type 'Admin'.
    It fetches all records of hospital vaccines from the storage and creates a list containing details
    of vaccines and their quantities available at the specified hospital ID. This list is then returned
    in JSON format.

    Returns:
    - JSON response: A list of vaccine details and quantities available at the specified hospital ID.

    """
    if redirect_user('Admin'):
        return redirect_user('Admin')
    data = json.loads(request.data)
    hospital_vaccines = storage.all(Hospital_Vaccine).values()
    vaccines_list = []
    for hospital in hospital_vaccines:
        if hospital.hospital_id == data['id']:
            vaccine = storage.get_by_id(Vaccine, hospital.vaccine_id)
            vaccines_list.append({'denomination': vaccine.denomination,
                                  'quantity': hospital.quantity})
    return jsonify(vaccines_list)


@app_views.route('/hospital/add-vaccine', methods=['POST'])
@login_required
def hospital_add_vaccine():
    """
    Adds a vaccine to a hospital's inventory.

    Adds a vaccine to a hospital's inventory based on the provided data in the request.
    The function ensures that only users who are of type 'Nurse' can access this functionality.
    It retrieves the hospital and vaccine using the provided IDs from the request data. If the vaccine
    already exists in the hospital's inventory, it returns a JSON response indicating its existence.
    Otherwise, it appends the vaccine to the hospital's vaccines list, updates the vaccine's stock,
    saves the changes, and returns an empty JSON response upon successful addition.

    Returns:
    - An empty JSON response upon successfully adding the vaccine to the hospital's inventory.

    """
    if redirect_user('Nurse'):
        return redirect_user('Nurse')
    data = json.loads(request.data)
    hospital = storage.get_by_id(Hospital, data.get('hospital_id'))
    vaccine = storage.get_by_id(Vaccine, data.get('vaccine_id'))
    if vaccine in hospital.vaccines:
        return jsonify({ 'status': 'Exist'})
    hospital.vaccines.append(vaccine)
    vaccine.stock += int(data.get('stock'))
    storage.save()
    return jsonify({})
