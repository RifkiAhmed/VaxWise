#!/usr/bin/python3
"""
This module handles views and routes for the Flask application, including admin_home, user_home, nurse_home, 
user_profile, user_contact, nurse_profile, nurse_contact and rendering templates for the application's user interface.

"""
from flask import jsonify, render_template, request
from flask_login import current_user, login_required
import json
from models import storage
from models.tables import *
from modules.redirect_user import redirect_user
from modules.send_email import send_email
import os
from views import app_views


@app_views.route('/admin', methods=['GET'])
@login_required
def admin_home():
    """
    Renders the admin dashboard.

    Renders the 'admin-1.html' template, displaying the admin dashboard with various statistics
    and information. The function ensures the user is redirected if they are not of type 'Admin'.
    It fetches information regarding hospitals, nurse counts by hospital, counts of vaccinated
    children, and overall statistics including the count of nurses, parents, and children in the system.
    This information is sent to the 'admin-1.html' template for display.

    Returns:
    - Renders the 'admin-1.html' template with statistics, hospital information, and user data
      for the admin dashboard.

    """
    if redirect_user('Admin'):
        return redirect_user('Admin')
    hospitals = storage.all(Hospital).values()
    nurses_count = nurses_by_hospital()
    nurses_count = json.dumps(nurses_count)
    children = vaccinated_children()
    children = json.dumps(children)
    statistics = {
        'nurses': storage.count(Nurse),
        'parents': storage.count(User) - 1,
        'childs': storage.count(Child),
    }
    return render_template("admin-1.html", user=current_user,
                           hospitals=hospitals, statistics=statistics,
                           nurses_count=nurses_count,
                           vaccine_status=vaccine_stock(),
                           vaccinated_child=children)


@app_views.route('/', methods=['GET'])
@app_views.route('/home', methods=['GET'])
@login_required
def user_home():
    """
    Renders the user home page.

    Renders the 'user-1.html' template displaying the home page for a user. The function ensures
    the user is redirected if they are not of type 'User'. It fetches all doses from storage, sorts
    them alphabetically by denomination, and sends the sorted list of doses along with the current
    user's information to the 'user-1.html' template for rendering.

    Returns:
    - Renders the 'user-1.html' template with the sorted list of doses and the current user's
      information for display on the home page.

    """
    if redirect_user('User'):
        return redirect_user('User')
    doses = storage.all(Dose).values()
    sorted_doses = sorted(doses, key=lambda dose: dose.denomination)
    return render_template("user-1.html", user=current_user, doses=sorted_doses)


@app_views.route('/nurse/home', methods=['GET'])
@login_required
def nurse_home():
    """
    Renders the home page for nurses.

    Renders the 'nurse-1.html' template, displaying the home page for nurses.
    The function ensures that only authenticated users with the 'Nurse' role can access this functionality.
    It retrieves information about hospital vaccines, hospital details, children, and doses, sorts them appropriately,
    and renders the nurse's home page with the necessary information.

    Returns:
    - Renders the 'nurse-1.html' template displaying the home page for nurses with relevant information.

    """
    if redirect_user('Nurse'):
        return redirect_user('Nurse')
    hospitals_vaccines = storage.all(Hospital_Vaccine).values()
    hospital = storage.get_by_id(Hospital, current_user.hospital_id)
    hospital_vaccines = {}
    for vaccine in hospitals_vaccines:
        if vaccine.hospital_id == hospital.id:
            denomination = storage.get_by_id(Vaccine, vaccine.vaccine_id).denomination
            hospital_vaccines[denomination] = {'hospital_id': hospital.id,
                                               'vaccine_id': vaccine.vaccine_id,
                                               'quantity': vaccine.quantity}
    children = storage.all(Child).values()
    doses = storage.all(Dose).values()
    sorted_children = sorted(children, key=lambda child: child.first_name)
    sorted_doses = sorted(doses, key=lambda dose: dose.denomination)
    sorted_vaccines = {k: hospital_vaccines[k] for k in sorted(hospital_vaccines)}
    return render_template("nurse-1.html", user=current_user,
                           hospital_vaccines=sorted_vaccines,
                           childs=sorted_children, doses=sorted_doses,
                           hospital_name=hospital.name)


@app_views.route('/user/profile', methods=['GET'])
@login_required
def user_profile():
    """
    Renders the profile page for the logged-in user.

    Renders the 'user-3.html' template, displaying the profile page for the logged-in user.
    The function ensures that only authenticated users can access this functionality.
    If the user is not of type 'User', it redirects them to the appropriate page.

    Returns:
    - Renders the 'user-3.html' template displaying the profile page for the logged-in user.

    """
    if redirect_user('User'):
        return redirect_user('User')
    return render_template("user-3.html", user=current_user)


@app_views.route('/nurse/profile', methods=['GET'])
@login_required
def nurse_profile():
    """
    Renders the nurse's profile page.

    Renders the 'nurse-3.html' template, displaying the profile page for the nurse. The function ensures
    the user is redirected if they are not of type 'Nurse'. It retrieves the nurse's associated hospital
    information and sends it along with the current user's data to the 'nurse-3.html' template for display
    on the profile page.

    Returns:
    - Renders the 'nurse-3.html' template with the nurse's and associated hospital's information for display
      on the profile page.

    """
    if redirect_user('Nurse'):
        return redirect_user('Nurse')
    hospital = storage.get_by_id(Hospital, current_user.hospital_id)
    return render_template("nurse-3.html", user=current_user,
                           hospital=hospital)


@app_views.route('/user/contact', methods=['GET'])
@login_required
def user_contact():
    """
    Renders the contact page for the logged-in user.

    Renders the 'user-4.html' template, displaying the contact page for the logged-in user.
    The function ensures that only authenticated users can access this functionality.
    If the user is not of type 'User', it redirects them to the appropriate page.

    Returns:
    - Renders the 'user-4.html' template displaying the contact page for the logged-in user.

    """
    if redirect_user('User'):
        return redirect_user('User')
    return render_template("user-4.html", user=current_user)


@app_views.route('/nurse/contact', methods=['GET'])
@login_required
def nurse_contact():
    """
    Renders the contact page for nurses.

    Renders the 'nurse-4.html' template, which displays the contact form for nurses.
    The function ensures the user is redirected if they are not of type 'Nurse'. It returns the 'nurse-4.html'
    template.

    Returns:
    - Renders the 'nurse-4.html' template designed for nurses.

    """
    if redirect_user('Nurse'):
        return redirect_user('Nurse')
    return render_template("nurse-4.html", user=current_user)


@app_views.route('/contact', methods=['POST'])
@login_required
def contact():
    """
    Sends a user or nurse message to the platform administrators.

    Sends a message from either a user or a nurse to the platform administrators based on the provided
    email address. The function retrieves the user or nurse based on the email provided in the request
    data. It constructs an HTML email message containing the sender's full name, email address, subject,
    and message content. This message is sent to the platform administrators' email address. Finally,
    it returns a JSON response indicating the successful sending of the message.

    Returns:
    - JSON response: {'status': 'Message sent successfully, Thank you!.'} after sending the message.

    """
    data = json.loads(request.data)
    user = storage.get_by_email(User, data['email'])
    nurse = storage.get_by_email(Nurse, data['email'])
    sender_full_name = ''
    if user:
        subject = 'VaxWise APP - User message'
        sender_full_name = user.first_name + ' ' + user.last_name
    else:
        subject = 'VaxWise APP - Nurse message'
        sender_full_name = nurse.first_name + ' ' + nurse.last_name

    html_content = f"""
    <html>
        <body>
            <h1>VaxWise APP</h1>
            <h5 style="font-size:16px;">Message from "{sender_full_name}"; email address: <strong>{data['email']}</strong></h5>
            <h6 style="font-size:16px; display: inline-block;">Subject: &nbsp;</h6>
            <p style="font-size:16px; display: inline-block;">{data['subject']}</p><br />
            <h6 style="font-size:16px; margin: 0px;">Message:</h6>
            <p style="font-size:16px; margin: 0px;">{data['message']}</p>
        </body>
    </html>
    """
    send_email(subject, html_content, os.getenv('ADMIN_USERNAME'))
    return jsonify({'status': 'Message sent successfully, Thank you!.'})


def nurses_by_hospital():
    """
    Counts the number of nurses per hospital.

    Counts the number of nurses associated with each hospital in the system. It retrieves all hospitals
    and nurses from storage, iterates through each hospital, and counts the nurses linked to that
    particular hospital. The function creates a list of tuples containing hospital names and their
    respective nurse counts, sorted alphabetically by hospital name, and returns this list.

    Returns:
    - A sorted list of tuples containing hospital names and the number of nurses associated with each
      hospital in the system.

    """
    hospitals = storage.all(Hospital).values()
    nurses = storage.all(Nurse).values()
    nurses_count = []
    
    for hospital in hospitals:
        number_nurses = 0
        for nurse in nurses:
            if hospital.id in nurse.hospital_id:
                number_nurses += 1
        nurses_count.append((hospital.name, number_nurses))
    return sorted(nurses_count)


def vaccine_stock():
    """
    Checks and categorizes the stock status of vaccines.

    Checks the stock level of each vaccine in the system and categorizes them based on predefined
    thresholds. It retrieves all vaccines from storage, sets thresholds for low stock and surplus,
    then iterates through each vaccine, determining its stock status (Low, Surplus, or Adequate).
    The function creates a dictionary containing vaccine denominations as keys and their respective
    stock levels and statuses. It sorts this dictionary alphabetically by vaccine denomination and
    returns the sorted dictionary.

    Returns:
    - A sorted dictionary containing vaccine denominations as keys and their respective stock levels
      along with categorized statuses (Low, Surplus, or Adequate).

    """
    vaccines = storage.all(Vaccine).values()
    low_stock_threshold = 500
    surplus_threshold = 2000
    vaccine_stock = {}

    for vaccine in vaccines:
        vaccine_data = {}
        vaccine_data['stock'] = vaccine.stock
        if vaccine.stock < low_stock_threshold:
            vaccine_data['status'] = 'Low'
        elif vaccine.stock > surplus_threshold:
            vaccine_data['status'] = 'Surplus'
        else:
            vaccine_data['status'] = 'Adequate'
        vaccine_stock[vaccine.denomination] = vaccine_data
    sorted_dict = {k: vaccine_stock[k] for k in sorted(vaccine_stock)}
    return sorted_dict


def vaccinated_children():
    """
    Counts the number of vaccinated children per dose.

    Counts the number of children who have received each dose in the system. It retrieves all doses and
    children from storage, iterates through each dose, and counts the number of children who have received
    that particular dose. The function creates a list of tuples containing dose denominations and the
    respective counts of vaccinated children for each dose, sorted alphabetically by dose denomination,
    and returns this sorted list.

    Returns:
    - A sorted list of tuples containing dose denominations and the number of children who have received
      each dose in the system.

    """
    doses = storage.all(Dose).values()
    children = storage.all(Child).values()
    vaccinated_children = []
    
    for dose in doses:
        number_children = 0
        for child in children:
            if dose in child.doses:
                number_children += 1
        vaccinated_children.append((dose.denomination, number_children))
    return sorted(vaccinated_children)
