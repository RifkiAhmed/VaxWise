#!/usr/bin/python3
"""
This module handles views and routes for the Flask application, including sign-up, login, logout,
email verification, and rendering templates for the application's user interface.

"""
from flask import jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
import json
from models import storage
from models.tables import *
from modules.send_email import send_email
import os
import uuid
from views import app_views
from werkzeug.security import check_password_hash, generate_password_hash


@app_views.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    """
    Registers a new user.

    If the HTTP request method is 'POST', it extracts user information from the request data 
    (including email, first name, last name, and password). It checks if the provided email 
    already exists in the system for either a User or Nurse. If the email is not found, it 
    creates a new User instance, hashes the password, saves it to storage, sends a verification 
    email, and redirects to the verification page. If the email already exists, it returns an 
    error message indicating the email is already in use. If the request method is 'GET', 
    it renders the sign-up page.

    Returns:
        - JSON response: {'status': 'Error', 'message': 'Email already exists.'} if the email is 
          already in use.
        - JSON response: {'href': '/verification'} if the sign-up is successful and a 
          verification email is sent.
        - Renders 'sign-up.html' template if the HTTP request method is 'GET'.

    """
    if request.method == 'POST':
        data = json.loads(request.data)
        kwargs = {
            'id': str(uuid.uuid4()),
            'email': data['email'].lower(),
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'password': data['password'],
            'status': 'unverified',
        }
        user = storage.get_by_email(User, kwargs['email'])
        nurse = storage.get_by_email(Nurse, kwargs['email'])
        if user or nurse:
            return jsonify({'status': 'Error',
                            'message': 'Email already exists.'})
        else:
            kwargs['password'] = generate_password_hash(kwargs['password'],
                                                        method='pbkdf2:sha256')
            new_user = User(**kwargs)
            storage.new(new_user)
            storage.save()
            verify_email(new_user)
            return jsonify({'href': '/verification'})
    return render_template("sign-up.html", user=current_user)


@app_views.route('/login', methods=['GET', 'POST'])
def login():
    """
    Logs in a user or nurse based on provided credentials.

    If the HTTP request method is 'POST', it extracts user credentials from the request data
    (email and password). It checks if the provided email exists for either a User or Nurse.
    If a Nurse is found, it verifies the provided password and nurse status, sending a verification
    email if not verified, and logs in the nurse, redirecting to the nurse home page if successful.
    If a User is found, it verifies the provided password and user status, sending a verification
    email if not verified, and logs in the user. If the user is the admin, it redirects to the admin
    page; otherwise, it redirects to the user home page. If credentials are incorrect or not found, it
    returns an error message. If the request method is 'GET', it renders the login page.

    Returns:
        - JSON response: {'href': '/verification'} if a nurse or user needs verification.
        - JSON response: {'href': '/'} if a regular user successfully logs in.
        - JSON response: {'href': '/admin'} if the user logging in is the admin.
        - JSON response: {'href': '/nurse/home'} if a nurse successfully logs in.
        - JSON response: {'status': 'Error', 'message': 'Incorrect email or password, try again.'}
          if credentials are incorrect or not found.
        - Renders 'login.html' template if the HTTP request method is 'GET'.
    """
    if request.method == 'POST':
        data = json.loads(request.data)
        email = data['email'].lower()
        password = data['password']
        user = storage.get_by_email(User, email)
        nurse = storage.get_by_email(Nurse, email)        
        if nurse:
            if check_password_hash(nurse.password, password):
                if nurse.status != 'verified':
                    verify_email(nurse)
                    return jsonify({'href': '/verification'})
                login_user(nurse, remember=True)
                return jsonify({'href': '/nurse/home'})
            else:
                return jsonify({'status': 'Error',
                                'message': 'Incorrect email or password, try again.'})
        elif user:
            if check_password_hash(user.password, password):
                if user.status != 'verified':
                    verify_email(user)
                    return jsonify({'href': '/verification'})
                login_user(user, remember=True)
                if email == os.getenv('ADMIN_EMAIL').lower():
                    return jsonify({'href': '/admin'})
                return jsonify({'href': '/'})
            else:
                return jsonify({'status': 'Error',
                                'message': 'Incorrect email or password, try again.'})
        else:
            return jsonify({'status': 'Error',
                            'message': 'Incorrect email or password, try again.'})
    return render_template("login.html", user=current_user)


@app_views.route('/logout')
@login_required
def logout():
    """
    Logs out the current user.

    Performs a logout action by invoking the logout_user() function from the
    Flask-Login extension to terminate the current user session. 
    It then redirects the user to the login page of the application.

    Returns:
        - Redirects to the login page.

    """
    logout_user()
    return redirect(url_for('app_views.login'))


@app_views.route('/verify/<receiver_email>/<receiver_token>', methods=['GET'])
def verify_email_token(receiver_email, receiver_token):
    """
    Verifies the email status using a token.

    Retrieves the user or nurse based on the received token. If a user is found, it updates the user's
    status to 'verified' in the storage system. If a nurse is found, it updates the nurse's status
    similarly. It then re-fetches the user or nurse using the receiver's email and sends a verification
    email again if the user or nurse is found. Finally, it redirects to the 'status' endpoint in the app.

    Arguments:
    - receiver_email: The email of the user or nurse receiving the token.
    - receiver_token: The token used for verification.

    Returns:
    - Redirects to the 'status' endpoint in the app after updating the status and possibly re-sending
      the verification email.
    """
    user = storage.get_by_token(User, receiver_token)
    nurse = storage.get_by_token(Nurse, receiver_token)
    if user:
        user.status = 'verified'
        storage.save()
    elif nurse:
        nurse.status = 'verified'
        storage.save()
    user = storage.get_by_email(User, receiver_email)
    nurse = storage.get_by_email(Nurse, receiver_email)   
    if user:
        verify_email(user)
    elif nurse:
        verify_email(nurse)
    return redirect(url_for('app_views.status'))


@app_views.route('/verification')
def verification():
    """
    Renders the email verification notification page.

    Renders the 'verification.html' template, which serves as a notification page indicating that
    an email for verification has been sent to the user or nurse.

    Returns:
    - Renders the 'verification.html' template indicating that an email for verification has been sent.
    """
    return render_template('verification.html')


@app_views.route('/status')
def status():
    """
    Renders the verification success page.

    Renders the 'status.html' template, which serves as a page to inform users or nurses that
    the verification process has been successfully completed.

    Returns:
    - Renders the 'status.html' template indicating successful verification.
    """
    return render_template('status.html')


def verify_email(user):
    """
    Sends an email with a verification link to the user or nurse.

    Generates a verification token, saves it to the provided user or nurse's data, and constructs an email
    with a verification link that directs them to verify their email address. The email is sent to the
    respective user or nurse's email address.

    Arguments:
    - user: An instance of the User or Nurse model representing the individual to whom the verification
      email will be sent.

    """
    import secrets
    token = secrets.token_urlsafe(16)
    user.token = token
    storage.save()
    verification_link = url_for('app_views.verify_email_token', receiver_email=user.email, receiver_token=token, _external=True)
    subject = 'VaxWise APP Email Verification'
    html_content=f"""
    <html>
        <body style="text-align:center">
            <br />
            <h1>VaxWise APP</h1>
            <strong style="font-size:18px; display: block;">Welcome to our platform!</strong>
            <p style="font-size:16px;">To get started, please verify your email address by clicking the link below:</p>
            <a href="{verification_link}"  style="font-size:16px; display: block;">Verify Email</a>
            <p  style="font-size:16px;">If you did not sign up for our platform, please ignore this email.</p><br />
            <p style="font-size:16px;">Thank you!</p>
        </body>
    </html>
    """
    send_email(subject, html_content, user.email)
