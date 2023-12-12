#!/usr/bin/python3
"""
This module handles views and routes for the Flask application, including get_vaccine,
implement_stock, vaccination_tracker, admin_vaccines_table, nurse_vaccines_table,
index_vaccines_table and rendering templates for the application's user interface.

"""
from datetime import datetime
from flask import jsonify, render_template, request
from flask_login import current_user, login_required
from models.tables import *
from models import storage
from modules.redirect_user import redirect_user
import os
from views import app_views


@app_views.route('/vaccine/<id>', methods=['GET'])
@login_required
def get_vaccine(id):
    """
    Retrieves vaccine information by ID.

    Retrieves and returns information about a specific vaccine based on the provided ID.
    The function ensures that only authenticated users can access this functionality.
    If the user is not the admin, it provides limited information about the vaccine, including its denomination,
    description, and a list of doses associated with the vaccine.
    For admin users, it returns the full details of the vaccine.

    Args:
    - id (str): The ID of the vaccine to retrieve information.

    Returns:
    - JSON object containing vaccine information based on the user's role:
        - For admin users: Full details of the vaccine.
        - For non-admin users: Limited information including denomination, description, and associated doses.
    """
    vaccine = storage.get_by_id(Vaccine, id)
    if vaccine:
        user = storage.get_by_id(User, current_user.id)
        if user and user.email != os.getenv('ADMIN_USERNAME'):
            dose_list = []
            doses = storage.all(Dose).values()
            sorted_doses = sorted(doses, key=lambda dose: dose.denomination)            
            for dose in sorted_doses:
                if dose.vaccine_id == vaccine.id:
                    dose_list.append([dose.denomination, dose.term])
            return jsonify({'denomination': vaccine.denomination, 'description': vaccine.description, 'doses': dose_list})
        return jsonify(vaccine.to_dict())
    return jsonify({})


# @app_views.route('/vaccine', methods=['POST'])
# @login_required
# def create_vaccine():
#     """  docstring  """
#     if redirect_user('Nurse'):
#         return redirect_user('Nurse')
#     kwargs = {
#         'id': str(uuid.uuid4()),
#         'denomination': request.form.get('dci'),
#         'term': request.form.get('term'),
#         'stock': request.form.get('stock')
#     }
#     if kwargs['denomination'] is None:
#         flash('Add Vaccin denomination!', category='error')
#     if kwargs['term'] is None:
#         flash('Add Vaccin Term!', category='error')
#     else:
#         new_vaccine = Vaccine(**kwargs)
#         hospital = storage.get(Hospital, current_user.hospital_id)
#         hospital.vaccines.append(new_vaccine)
#         storage.new(new_vaccine)
#         storage.save()
#     return redirect(url_for('app_views.nurse_home'))


# @app_views.route('/vaccine', methods=['DELETE'])
# @login_required
# def delete_vaccine():
#     """  docstring  """
#     if redirect_user('Nurse'):
#         return redirect_user('Nurse')
#     vaccin = json.loads(request.data)
#     vaccin = storage.get(Vaccine, vaccin['vaccinId'])
#     if vaccin:
#         storage.delete(vaccin)
#         storage.save()
#     return jsonify({})


@app_views.route('/dose/<id>/range/<range>', methods=['GET'])
@login_required
def vaccination_tracker(id, range):
    """
    Projects future vaccinations for a specific dose within a provided time period.

    Retrieves information to project the future vaccinations for a specific dose based on the provided dose ID
    and the time period in days. The function ensures that only users who are of type 'Nurse' can access this functionality.
    The function calculates the potential number of children eligible for the specified dose within the provided time period,
    indicating the projected vaccinations needed.

    Arguments:
    - id: The ID of the dose to project future vaccinations for.
    - period: The time period (in days) within which future vaccinations are projected.

    Returns:
    - JSON response with details about the specified dose and the projected number of vaccinations required
      for the provided time period.

    """
    if redirect_user('Nurse'):
        return redirect_user('Nurse')
    dose = storage.get_by_id(Dose, id)
    children = storage.all(Child).values()
    vaccination = 0
    for child in children:
        age_in_days = (datetime.now() - child.birthdate).days + 1
        if age_in_days + int(range) >= dose.term:
            vaccination += 1
    return jsonify({ 'dose': dose.denomination, 'vaccination': vaccination})


@app_views.route('/hospital/<hospital_id>/vaccine/<vaccine_id>/<quantity>',
                 methods=['PUT'])
@login_required
def implement_stock(hospital_id, vaccine_id, quantity):
    """
    Updates vaccine stock for a hospital.

    Modifies the stock quantity of a particular vaccine available at a specified hospital.
    The function ensures that only users who are of type 'Nurse' can access this functionality.
    The function retrieves existing hospital-vaccine relationships and increases the stock
    quantity of a specific vaccine in the specified hospital by the provided quantity.
    After updating the stock quantity, the changes are saved to the storage.

    Arguments:
    - hospital_id: The ID of the hospital where the vaccine stock is updated.
    - vaccine_id: The ID of the vaccine for which the stock is updated.
    - quantity: The quantity by which the vaccine stock is increased.

    Returns:
    - Empty JSON response to indicate the successful update of the vaccine stock.

    """
    if redirect_user('Nurse'):
        return redirect_user('Nurse')
    hospital_vaccines = storage.all(Hospital_Vaccine).values()
    for vaccine in hospital_vaccines:
        if vaccine.hospital_id == hospital_id and vaccine.vaccine_id == vaccine_id:
            vaccine.quantity += int(quantity)
            break
    storage.save()
    vaccine = storage.get_by_id(Vaccine, vaccine_id)
    if vaccine:
        vaccine.stock += int(quantity)
        storage.save()
    return jsonify({})


@app_views.route('/vaccines', methods=['GET'])
@login_required
def admin_vaccines_table():
    """
    Renders the vaccines table.

    Retrieves the referring URL from the request and renders the 'admin-4.html' template.
    The template displays the vaccines table and includes a back button URL for navigation.
    This function is accessible to administrators.

    Returns:
    - Renders the 'admin-4.html' template displaying the vaccines table and navigation controls.

    """
    if redirect_user('Admin'):
        return redirect_user('Admin')
    referring_url = request.referrer
    return render_template("admin-4.html", back_url=referring_url,
                           user=current_user)


@app_views.route('/nurse/vaccines-table', methods=['GET'])
@login_required
def nurse_vaccines_table():
    """
    Renders a static vaccination schedule page for nurses.

    Renders a static HTML page ('nurse-2.html') that displays the vaccination schedule. The function ensures
    the user is redirected if they are not of type 'Nurse'.

    Returns:
    - Renders the 'nurse-2.html' template, which contains the static vaccination schedule.

    """
    if redirect_user('Nurse'):
        return redirect_user('Nurse')
    return render_template("nurse-2.html", user=current_user)


@app_views.route('/vaccines-table', methods=['GET'])
def index_vaccines_table():
    """
    Renders the vaccines table page.

    Retrieves the referring URL from the request and renders the 'vaccines-table.html' template.
    The template displays the vaccines table and includes a back button URL for navigation.

    Returns:
    - Renders the 'vaccines-table.html' template displaying the vaccines table and navigation controls.

    """
    referring_url = request.referrer
    return render_template("vaccines-table.html", back_url=referring_url,
                           user=current_user)
