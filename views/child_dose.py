#!/usr/bin/python3
"""
This module handles child_vaccination view and route for the Flask application.
"""
from flask import jsonify
from flask_login import login_required
from models import storage
from models.tables import *
from modules.redirect_user import redirect_user
from views import app_views


@app_views.route('/hospital/<hospital_id>/child/<child_id>/dose/<dose_id>',
                 methods=['GET'])
@login_required
def child_vaccination(hospital_id, child_id, dose_id):
    """
    Manages child vaccination record.

    Manages the vaccination record for a child in a hospital for a specific dose. The function ensures
    the user is redirected if they are of type 'Nurse'. It retrieves information about the child,
    dose, and vaccine based on the provided IDs. It checks if the child has already received the dose;
    if not, it adds the dose to the child's vaccination record and updates the vaccine stock accordingly.
    It also updates the quantity of the specific vaccine in the hospital's inventory if it exists.

    Arguments:
    - hospital_id: The ID of the hospital where the vaccination is being recorded.
    - child_id: The ID of the child receiving the vaccination.
    - dose_id: The ID of the specific dose being administered.

    Returns:
    - JSON response: {'status': 'Exist'} if the child has already received the dose.
    - An empty JSON response after successfully adding the dose to the child's records and updating
      vaccine and hospital inventory quantities.

    """
    if redirect_user('Nurse'):
        return redirect_user('Nurse')
    child = storage.get_by_id(Child, child_id)
    dose = storage.get_by_id(Dose, dose_id)
    if child and dose:
        vaccine = storage.get_by_id(Vaccine, dose.vaccine_id)
        if dose in child.doses:
            return jsonify({'status': 'Exist'})
        else:
            child.doses.append(dose)
            vaccine.stock -= 1
            storage.save()
    hospital_vaccines = storage.all(Hospital_Vaccine).values()
    for item in hospital_vaccines:
        if item.hospital_id == hospital_id and item.vaccine_id == vaccine.id:
            item.quantity -= 1
            storage.save()
    return jsonify({})
