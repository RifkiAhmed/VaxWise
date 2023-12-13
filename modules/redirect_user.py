#!usr/bin/python3

def redirect_user(currentuser):
    """Redirects users based on their roles.

    Args:
    - currentuser: Object representing the current user.

    Returns:
    - Redirects to different views based on user roles:
      - If currentuser is 'Admin' and (user or nurse) exists:
        - If currentuser's email is not the admin email, redirects to user's home.
        - If nurse exists, redirects to nurse's home.
      - If currentuser is 'User' and (user or nurse) exists:
        - If currentuser's email is the admin email, redirects to admin's home.
        - If nurse exists, redirects to nurse's home.
      - If conditions do not match, redirects based on currentuser's email:
        - If currentuser's email is the admin email, redirects to admin's home.
        - If currentuser's email is not the admin email, redirects to user's home.

    If no redirection matches the conditions, returns None.
    """
    from flask import redirect, url_for
    from flask_login import current_user
    from models import storage
    from models.tables import Nurse, User
    import os
    user = storage.get_by_id(User, current_user.id)
    nurse = storage.get_by_id(Nurse, current_user.id)
    if currentuser == 'Admin' and (user or nurse):
        if user and user.email != os.getenv('ADMIN_EMAIL'):
            return redirect(url_for('app_views.user_home'))
        elif nurse:
            return redirect(url_for('app_views.nurse_home'))
    elif currentuser == 'User' and (user or nurse):
        if user and user.email == os.getenv('ADMIN_EMAIL'):
            return redirect(url_for('app_views.admin_home'))
        elif nurse:
            return redirect(url_for('app_views.nurse_home'))
    else:
        if user and user.email == os.getenv('ADMIN_EMAIL'):
            return redirect(url_for('app_views.admin_home'))
        elif user and user.email != os.getenv('ADMIN_EMAIL'):
            return redirect(url_for('app_views.user_home'))
    return None
