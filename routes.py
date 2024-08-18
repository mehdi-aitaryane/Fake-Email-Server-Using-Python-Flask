import logging
from flask import render_template, request, redirect, url_for, flash, session
from flask_login import UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
from models import *
from forms import *
from configs import app, login_manager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



@login_manager.user_loader
def load_user(user_id):
    logger.info(f"Loading user with ID: {user_id}")
    return User.query.get(int(user_id))

# Function to delete messages older than one hour
def delete_old_messages():
    logger.info("Deleting messages older than one hour.")
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    old_messages = Message.query.filter(Message.date <= one_hour_ago).all()
    for message in old_messages:
        db.session.delete(message)
        logger.info(f"Deleted message with ID: {message.id}")
    db.session.commit()

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        logger.info(f"User {current_user.email} is attempting to change their password.")
        current_user.set_password(form.new_password.data)  # Hash the new password
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        logger.info(f"User {current_user.email} changed their password successfully.")
        session['success'] = '<strong>Profile updated successfully</strong>'
        return redirect(url_for('inbox'))
        
    return render_template('change_password.html', form=form)

@app.route('/change-info', methods=['GET', 'POST'])
@login_required
def change_profile():
    form = ProfileForm()
    if form.validate_on_submit():
        logger.info(f"User {current_user.email} is attempting to update profile information.")
        existing_user = User.query.filter_by(email=form.email.data).first()
        
        if existing_user and current_user.email != form.email.data:
            flash('Email address already exists.', 'danger')
            logger.warning(f"Email address {form.email.data} already exists.")
        else:
            current_user.first_name = form.first_name.data
            current_user.last_name = form.last_name.data
            current_user.email = form.email.data
            db.session.commit()
            flash('Profile updated successfully.', 'success')
            logger.info(f"User {current_user.email} updated their profile successfully.")
            session['success'] = '<strong>Profile updated successfully</strong>'
            return redirect(url_for('inbox'))

    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email
    return render_template('change_info.html', form=form)

@app.route('/not_found')
def not_found():
    logger.info("404 Not Found error page.")
    return render_template('not_found.html')

@app.route('/unauthorised_access')
def unauthorised_access():
    logger.info("401 Unauthorised Access error page.")
    return render_template('unauthorised_access.html')


@app.route('/')
def index():
    if current_user.is_authenticated:
        logger.info(f"User {current_user.email} is already authenticated, redirecting to inbox.")
        return redirect(url_for('inbox'))
    else:
        logger.info("User not authenticated, redirecting to login.")
        return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        logger.info("Attempting to register a new user.")
        existing_user = User.query.filter_by(email=form.email.data).first()
        
        if existing_user:
            flash('Email address already exists.', 'danger')
            logger.warning(f"Registration failed: Email {form.email.data} already exists.")
        else:
            new_user = User(first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data)
            new_user.set_password(form.password.data)  # Hash the password
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully. Please log in.', 'success')
            logger.info(f"New user registered with email: {form.email.data}")
            session['success'] = '<strong>Account created successfully</strong>. Please log in.'
            return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None  # Initialize error variable
    success = session.pop('success', None)

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        logger.info(f"Attempting to log in user with email: {email}")
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            logger.info(f"User {user.id} logged in successfully.")
            session['success'] = '<strong>Logged in successfully</strong>'
            return redirect(url_for('inbox'))

        error = '<strong>Login failed</strong>. Check your email and password.'
        logger.warning(f"Login failed for email: {email}")

    return render_template('login.html', success=success, error=error)

@app.route('/logout')
@login_required
def logout():
    logger.info(f"User {current_user.email} is logging out.")
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/inbox')
@login_required
def inbox():
    logger.info(f"User {current_user.email} is accessing their inbox.")
    delete_old_messages()  # Call function to delete old messages
    
    # Check if there's a success message in the session
    success = session.pop('success', None)

    messages = Message.query.filter_by(recipient=current_user).order_by(Message.date.desc()).all()
    return render_template('inbox.html', messages=messages, success=success)

@app.route('/sent')
@login_required
def sent():
    logger.info(f"User {current_user.email} is accessing their sent messages.")
    messages = Message.query.filter_by(sender=current_user).order_by(Message.date.desc()).all()
    return render_template('sent.html', messages=messages)

@app.route('/message/<int:message_id>')
@login_required
def view_message(message_id):
    message = Message.query.get_or_404(message_id)
    logger.info(f"User {current_user.email} is viewing message with ID: {message_id}")
    if current_user == message.recipient or current_user == message.sender:
        return render_template('view_message.html', message=message)
    else:
        flash('You are not authorized to view this message.', 'danger')
        logger.warning(f"User {current_user.email} is not authorized to view message ID: {message_id}")
        return redirect(url_for('inbox'))

@app.route('/send', methods=['GET', 'POST'])
@login_required
def send_message():
    form = SendMessageForm()  # Create an instance of the form

    if form.validate_on_submit():
        recipient_email = form.recipient_email.data
        subject = form.subject.data
        body = form.body.data
        logger.info(f"User {current_user.email} is attempting to send a message.")
        recipient = User.query.filter_by(email=recipient_email).first()

        if recipient:
            new_message = Message(sender=current_user, recipient=recipient, subject=subject, body=body)
            db.session.add(new_message)
            db.session.commit()
            flash('Message sent successfully.', 'success')
            logger.info(f"User {current_user.email} sent a message to user {recipient.id}")
            session['success'] = '<strong>Email sent successfully</strong>'
            return redirect(url_for('inbox'))
        else:
            flash('Recipient not found.', 'danger')
            logger.warning(f"Recipient not found for email: {recipient_email}")

    return render_template('send_message.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
