#!/usr/bin/python3
"""
This module handles views and routes for the Flask application, including get_nurse, get_nurses, add_nurse,
delete_nurse, update_nurse, nurse_hospital and rendering templates for the application's user interface.

"""
from flask import jsonify, render_template, request, url_for
from flask_login import current_user, login_required, logout_user
import json
from models import storage
from models.tables import *
from modules.redirect_user import redirect_user
from modules.send_email import send_email
import uuid
from views import app_views
from werkzeug.security import generate_password_hash


@app_views.route('/nurse/<id>', methods=['GET'])
@login_required
def get_nurse(id):
    """
    Retrieves nurse information by ID.

    Retrieves and returns information about a nurse using the provided ID. The function fetches the nurse's
    details based on the given ID from storage. If the nurse exists, it also retrieves the associated hospital's
    name. The function then returns a JSON response containing the nurse's email, first name, last name, and
    the name of the hospital they are associated with, if available.

    Args:
    - id: The ID of the nurse to retrieve.

    Returns:
    - JSON response: Nurse information including email, first name, last name, and hospital name
      (if the nurse exists), or a status 'Not Exist' if the nurse is not found.

    """
    nurse = storage.get_by_id(Nurse, id)
    if nurse:
        hospital = storage.get_by_id(Hospital, nurse.hospital_id)
        return jsonify({'email': nurse.email,
                        'first_name': nurse.first_name,
                        'last_name': nurse.last_name,
                        'hospital': hospital.name})
    return jsonify({"status": "Not Exist"})


@app_views.route('/nurses', methods=['GET'])
@login_required
def get_nurses():
    """
    Renders the list of nurses for administrators.

    Renders the 'admin-3.html' template, displaying a list of nurses in the system. The function ensures
    the user is redirected if they are not of type 'Admin'. It fetches information about all hospitals and
    nurses from storage and sorts the nurses alphabetically by their first names. The sorted list of nurses
    along with hospitals and user data is sent to the 'admin-3.html' template for display.

    Returns:
    - Renders the 'admin-3.html' template with the sorted list of nurses, hospitals, and user information for
      display to administrators.

    """
    if redirect_user('Admin'):
        return redirect_user('Admin')
    hospitals = storage.all(Hospital).values()
    nurses = storage.all(Nurse).values()
    sorted_nurses = sorted(nurses, key=lambda nurse: nurse.first_name)
    return render_template("admin-3.html", nurses=sorted_nurses,
                           hospitals=hospitals,
                           user=current_user)


@app_views.route('/nurse', methods=['POST'])
@login_required
def add_nurse():
    """
    Adds a new nurse to the system by an Admin.

    Adds a new nurse to the system based on the provided data in the request. The function ensures
    that only users with 'Admin' privileges can access this functionality. It retrieves necessary information
    from the request data, generates a unique ID, hashes the nurse's password, creates a new Nurse instance,
    saves it to storage, and triggers a contact message to the new nurse's email. After adding the nurse,
    it fetches updated information about hospitals and nurses and renders the 'admin-3.html'
    template, displaying the updated list of nurses and hospitals for administrators.

    Returns:
    - Renders the 'admin-3.html' template with the updated list of nurses, hospitals, and user information
    for display to administrators after successfully adding the new nurse.

    """
    if redirect_user('Admin'):
        return redirect_user('Admin')
    data = json.loads(request.data)
    password = data['password']
    data['id'] = str(uuid.uuid4())
    data['status'] = 'unverified'
    data['password'] = generate_password_hash(data['password'],
                                              method='pbkdf2:sha256')
    new_nurse = Nurse(**data)
    storage.new(new_nurse)
    storage.save()
    contact_nurse(new_nurse, password, False)
    hospitals = storage.all(Hospital).values()
    nurses = storage.all(Nurse).values()
    return render_template("admin-3.html", nurses=nurses, hospitals=hospitals,
                           user=current_user)


@app_views.route('/nurse', methods=['DELETE'])
@login_required
def delete_nurse():
    """
    Deletes a nurse from the system by an Admin.

    Deletes a nurse from the system based on the provided nurse ID in the request data. The function ensures
    that only users with 'Admin' privileges can access this functionality. It retrieves the nurse using the
    given ID, deletes the nurse if found, and saves the changes to storage.

    Returns:
    - An empty JSON response after deleting the nurse (if found).

    """
    if redirect_user('Admin'):
        return redirect_user('Admin')
    data = json.loads(request.data)
    nurse = storage.get_by_id(Nurse, data['id'])
    if nurse:
        storage.delete(nurse)
        storage.save()
    return jsonify({})


@app_views.route('/nurse', methods=['PUT'])
@login_required
def update_nurse():
    """
    Updates nurse information in the system.

    Updates nurse information based on the provided data in the request. The function checks the user's type
    and ensures that users with 'Admin' or 'Nurse' privileges can access this functionality. It retrieves
    the nurse using the given ID, updates the provided information, and saves the changes to storage.
    Additionally, if the user performing the update is the same nurse being updated and their status is
    'unverified', the function triggers an email verification and logs them out, redirecting to the
    verification page. If the nurse's status is 'verified', the function sends a contact message to the
    nurse's email after the update. Finally, it fetches updated information about hospitals and nurses,
    rendering the 'admin-3.html' template with the updated list of nurses and hospitals for administrators.

    Returns:
    - Renders the 'admin-3.html' template with the updated list of nurses, hospitals, and user information
      for display to administrators after successfully updating nurse information.

    """
    if redirect_user('Admin') and redirect_user('Nurse'):
        return redirect_user('Admin')
    data = json.loads(request.data)
    nurse = storage.get_by_id(Nurse, data.get('id'))
    password = data['password']
    data['password'] = generate_password_hash(data['password'],
                                              method='pbkdf2:sha256')
    if 'id' in data:
        del data['id']
    if 'email' in data:
        data['status'] = 'unverified'
    for key, value in data.items():
        if key == 'hospital_id' and value == '0':
            continue
        setattr(nurse, key, value)
    storage.save()
    if nurse.id == current_user.id:
        if nurse.status != 'verified':
            from views.authentification import verify_email
            verify_email(nurse)
            logout_user()
            return jsonify({'href': '/verification'})
        return jsonify({'href': ''})
    if nurse.status == 'verified':
        contact_nurse(nurse, password, True)
    else:
        contact_nurse(nurse, password, False)
    hospitals = storage.all(Hospital).values()
    nurses = storage.all(Nurse).values()
    return render_template("admin-3.html", nurses=nurses, hospitals=hospitals,
                           user=current_user)


@app_views.route('/nurse/hospital', methods=['PUT'])
@login_required
def nurse_hospital():
    """
    Updates the hospital assigned to a nurse.

    Updates the hospital assignment for a nurse in the system based on the provided data in the request.
    The function ensures that only users with 'Admin' privileges can access this functionality. It retrieves
    the nurse using the given ID, updates the hospital assignment if the nurse is found, and saves the changes
    to storage. Finally, it fetches updated information about hospitals and nurses, rendering the 'admin-3.html'
    template with the updated list of nurses and hospitals for administrators.

    Returns:
    - Renders the 'admin-3.html' template with the updated list of nurses, hospitals, and user information
      for display to administrators after successfully updating the nurse's hospital assignment.

    """
    if redirect_user('Admin'):
        return redirect_user('Admin')
    data = json.loads(request.data)
    nurse = storage.get_by_id(Nurse, data.get('id'))
    if nurse: 
        setattr(nurse, 'hospital_id', data.get('hospital_id'))
        storage.save()
    hospitals = storage.all(Hospital).values()
    nurses = storage.all(Nurse).values()
    return render_template("admin-3.html", nurses=nurses, hospitals=hospitals,
                           user=current_user)


def contact_nurse(nurse, password, verified):
    """
    Sends account details to a nurse's email.

    Generates and assigns a unique token to the nurse, which is then used to create an email containing
    login credentials for the nurse. The email is sent either for account verification (if 'verified' is True)
    or for informing about an account created/update. It includes the nurse's login credentials and provides
    a link for email verification or login. The email is sent to the nurse's provided email address.

    Args:
    - nurse: Nurse object containing nurse information.
    - password: Password generated for the nurse's account.
    - verified: Boolean indicating if the nurse's account is verified.

    Returns:
    - None. Sends an email to the nurse's email address with account details.
    """
    import secrets
    token = secrets.token_urlsafe(16)
    nurse.token = token
    storage.save()
    subject = 'Your Account Credentials for VaxWise App'
    html_content = ''
    if verified:
        verification_link = url_for('app_views.login', _external=True)
        html_content = f"""
        <html>
            <body>
                <h1>VaxWise APP</h1>
                <p style="font-size:16px;"><b>Dear {nurse.first_name},</b></p>
                <p style="font-size:16px;">We are delighted to inform you that an account has been updated for you on VaxWise. Below are your login credentials:</p>
                <p style="font-size:16px;">Email Address: <b>{nurse.email}</b></p>
                <p style="font-size:16px;">Password: <b>{password}</b><br></p>
                <p style="font-size:16px;">For security reasons, we recommend changing your password after your initial login. Please ensure that you keep your login credentials confidential and do not share them with anyone.</p>
                <p style="font-size:16px;">To access your account, follow this link <a href="{verification_link}" style="font-size:16px;">here</a> .<br></p>
                <p style="font-size:16px;">Best regards,</p>
                <p style="font-size:16px;"><b>VaxWise Team</b></p>
            </body>
        </html>
        """        
    else:
        verification_link = url_for('app_views.verify_email_token', receiver_email=nurse.email, receiver_token=token, _external=True)
        html_content = f"""
        <html>
            <body>
                <h1>VaxWise APP</h1>
                <p style="font-size:16px;"><b>Dear {nurse.first_name},</b></p>
                <p style="font-size:16px;">We are delighted to inform you that an account has been created/updated for you on VaxWise. Below are your login credentials:</p>
                <p style="font-size:16px;">Email Address: <b>{nurse.email}</b></p>
                <p style="font-size:16px;">Password: <b>{password}</b><br></p>
                <p style="font-size:16px;">For security reasons, we recommend changing your password after your initial login. Please ensure that you keep your login credentials confidential and do not share them with anyone.</p>
                <p style="font-size:16px;">To access your account, follow this link <a href="{verification_link}" style="font-size:16px;">Verify Email</a> to verify your email address.<br></p>
                <p style="font-size:16px;">Best regards,</p>
                <p style="font-size:16px;"><b>VaxWise Team</b></p>
            </body>
        </html>
        """
    send_email(subject, html_content, nurse.email)
