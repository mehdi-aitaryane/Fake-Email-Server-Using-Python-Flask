from models import User
import string
from re import match
from flask_login import current_user


def validate_registration_data(data):
    errors = {}

    if 'first_name' not in data or not data['first_name']:
        errors['first_name'] = 'First Name is required.'

    if 'last_name' not in data or not data['last_name']:
        errors['last_name'] = 'Last Name is required.'

    if 'email' not in data or not data['email']:
        errors['email'] = 'Email is required.'
    elif not is_valid_email(data['email']):
        errors['email'] = 'Invalid email address.'
    else:
        user = User.query.filter_by(email=data['email']).first()
        if user:
            errors['email'] = 'Email is already in use.'

    if 'password' not in data or not data['password']:
        errors['password'] = 'Password is required.'
    else:
        password_errors = validate_password(data['password'])
        if password_errors:
            errors['password'] = password_errors

    return errors

def is_valid_email(email):
    # Use a simple regex or a library for email validation
    return match(r'^[^@]+@[^@]+\.[^@]+$', email)

def validate_password(password):
    password_errors = []
    
    if len(password) < 8:
        password_errors.append('Password must be at least 8 characters long.')
    
    if not any(char.isdigit() for char in password):
        password_errors.append('Password must have at least 1 number.')

    if not any(char.isupper() for char in password):
        password_errors.append('Password must have at least 1 uppercase letter.')

    if not any(char.islower() for char in password):
        password_errors.append('Password must have at least 1 lowercase letter.')

    if not any(char in string.punctuation for char in password):
        password_errors.append('Password must have at least 1 special character.')

    return password_errors if password_errors else None

def validate_change_password_data(data):
    errors = {}

    if 'old_password' not in data or not data['old_password']:
        errors['old_password'] = 'Old Password is required.'
    elif not current_user.check_password(data['old_password']):
        errors['old_password'] = 'Password Not Correct.'

    if 'new_password' not in data or not data['new_password']:
        errors['new_password'] = 'New Password is required.'
    else:
        password_errors = validate_password(data['new_password'])
        if password_errors:
            errors['new_password'] = password_errors

    if 'confirm_password' not in data or not data['confirm_password']:
        errors['confirm_password'] = 'Confirm Password is required.'
    elif data['confirm_password'] != data['new_password']:
        errors['confirm_password'] = 'Password Not Confirmed.'

    return errors

def validate_send_message_data(data):
    errors = {}

    if 'recipient_email' not in data or not data['recipient_email']:
        errors['recipient_email'] = 'Recipient Email is required.'
    elif not is_valid_email(data['recipient_email']):
        errors['recipient_email'] = 'Invalid email address.'
    else:
        user = User.query.filter_by(email=data['recipient_email']).first()
        if not user:
            errors['recipient_email'] = 'Recipient not found.'

    if 'subject' not in data or not data['subject']:
        errors['subject'] = 'Subject is required.'

    # 'body' can be optional as per the original form

    return errors

def validate_profile_data(data):
    errors = {}

    if 'first_name' not in data or not data['first_name']:
        errors['first_name'] = 'First Name is required.'

    if 'last_name' not in data or not data['last_name']:
        errors['last_name'] = 'Last Name is required.'

    if 'email' not in data or not data['email']:
        errors['email'] = 'Email is required.'
    elif not is_valid_email(data['email']):
        errors['email'] = 'Invalid email address.'
    else:
        user = User.query.filter_by(email=data['email']).first()
        if user and current_user.email != data['email']:
            errors['email'] = 'Email is already in use.'

    return errors
