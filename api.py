import logging
from flask import request, redirect, url_for, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
from models import *
from validations import *
from configs import app, login_manager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@login_manager.user_loader
def load_user(user_id):
    logger.info(f"Loading user with ID: {user_id}")
    return User.query.get(int(user_id))

def delete_old_messages():
    logger.info("Deleting messages older than one hour.")
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    old_messages = Message.query.filter(Message.date <= one_hour_ago).all()
    for message in old_messages:
        db.session.delete(message)
        logger.info(f"Deleted message with ID: {message.id}")
    db.session.commit()

@app.route('/api/change-password', methods=['PUT'])
@login_required
def api_change_password():
    data = request.get_json()
    logger.info(f"User {current_user.email} is attempting to change password.")
    errors = validate_change_password_data(data)
    if errors:
        logger.error(f"Password change validation errors: {errors}")
        return jsonify({'errors': errors}), 400

    current_user.set_password(data['new_password'])
    db.session.commit()
    logger.info(f"User {current_user.email} changed their password successfully.")
    return jsonify({'message': 'Password changed successfully.'}), 200

@app.route('/api/change-info', methods=['PUT'])
@login_required
def api_change_profile():
    data = request.get_json()
    logger.info(f"User {current_user.email} is attempting to update profile information.")
    errors = validate_profile_data(data)
    if errors:
        logger.error(f"Profile update validation errors: {errors}")
        return jsonify({'errors': errors}), 400

    current_user.first_name = data['first_name']
    current_user.last_name = data['last_name']
    current_user.email = data['email']
    db.session.commit()
    logger.info(f"User {current_user.email} updated their profile successfully.")
    return jsonify({'message': 'Profile updated successfully.'}), 200

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    logger.info("Attempting to register a new user.")
    errors = validate_registration_data(data)
    if errors:
        logger.error(f"Registration validation errors: {errors}")
        return jsonify({'errors': errors}), 400

    new_user = User(first_name=data['first_name'], last_name=data['last_name'], email=data['email'])
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()
    logger.info(f"New user registered with email: {data['email']}")
    return jsonify({'message': 'Account created successfully.'}), 201

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    logger.info(f"Attempting to log in user with email: {email}")
    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        login_user(user)
        logger.info(f"User {user.id} logged in successfully.")
        return jsonify({'message': 'Logged in successfully.'}), 200
    logger.warning(f"Login failed for email: {email}")
    return jsonify({'error': 'Login failed. Check your email and password.'}), 401

@app.route('/api/logout')
@login_required
def api_logout():
    logger.info(f"User {current_user.email} is logging out.")
    logout_user()
    return jsonify({'message': 'Logged out successfully.'}), 200

@app.route('/api/inbox')
@login_required
def api_inbox():
    logger.info(f"User {current_user.email} is accessing their inbox.")
    delete_old_messages()
    messages = Message.query.filter_by(recipient=current_user).order_by(Message.date.desc()).all()
    messages_data = [{'id': msg.id, 'subject': msg.subject, 'body': msg.body, 'date': msg.date} for msg in messages]
    return jsonify(messages=messages_data), 200

@app.route('/api/sent')
@login_required
def api_sent():
    logger.info(f"User {current_user.email} is accessing their sent messages.")
    messages = Message.query.filter_by(sender=current_user).order_by(Message.date.desc()).all()
    messages_data = [{'id': msg.id, 'subject': msg.subject, 'body': msg.body, 'date': msg.date} for msg in messages]
    return jsonify(messages=messages_data), 200

@app.route('/api/message/<int:message_id>')
@login_required
def api_view_message(message_id):
    message = Message.query.get_or_404(message_id)
    logger.info(f"User {current_user.email} is viewing message with ID: {message_id}")
    if current_user == message.recipient or current_user == message.sender:
        return jsonify({'id': message.id, 'subject': message.subject, 'body': message.body, 'date': message.date}), 200
    logger.warning(f"User {current_user.email} is not authorized to view message ID: {message_id}")
    return jsonify({'error': 'You are not authorized to view this message.'}), 403

@app.route('/api/send', methods=['POST'])
@login_required
def api_send_message():
    data = request.get_json()
    logger.info(f"User {current_user.email} is attempting to send a message.")
    errors = validate_send_message_data(data)
    if errors:
        logger.error(f"Message sending validation errors: {errors}")
        return jsonify({'errors': errors}), 400

    recipient = User.query.filter_by(email=data['recipient_email']).first()
    if recipient:
        new_message = Message(sender=current_user, recipient=recipient, subject=data['subject'], body=data.get('body'))
        db.session.add(new_message)
        db.session.commit()
        logger.info(f"User {current_user.email} sent a message to user {recipient.id}")
        return jsonify({'message': 'Message sent successfully.'}), 201
    logger.warning(f"Recipient not found for email: {data['recipient_email']}")
    return jsonify({'error': 'Recipient not found.'}), 404
