from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from wtforms import StringField, TextAreaField, PasswordField, SubmitField
from flask_wtf import FlaskForm
from flask_login import current_user
import string
from models import *


class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already in use.')

    def validate_password(self, password):

        if len(password.data) < 8:
            raise ValidationError('Password must be at least 8 characters long.')

        if not any(char.isdigit() for char in password.data):
            raise ValidationError('Password must have at least 1 number.')

        if not any(char.isupper() for char in password.data):
            raise ValidationError('Password must have at least 1 uppercase letter.')

        if not any(char.islower() for char in password.data):
            raise ValidationError('Password must have at least 1 lowercase letter.')

        if not any(char in string.punctuation for char in password.data):
            raise ValidationError('Password must have at least 1 special character.')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Change Password')
    
    def validate_old_password(self, old_password):
        if not current_user.check_password(old_password.data):
            raise ValidationError('Password Not Correct.')

    def validate_new_password(self, new_password):

        if len(new_password.data) < 8:
            raise ValidationError('Password must be at least 8 characters long.')

        if not any(char.isdigit() for char in new_password.data):
            raise ValidationError('Password must have at least 1 number.')

        if not any(char.isupper() for char in new_password.data):
            raise ValidationError('Password must have at least 1 uppercase letter.')

        if not any(char.islower() for char in new_password.data):
            raise ValidationError('Password must have at least 1 lowercase letter.')

        if not any(char in string.punctuation for char in new_password.data):
            raise ValidationError('Password must have at least 1 special character.')

    def validate_confirm_password(self, confirm_password):
        if confirm_password.data != self.new_password.data:
            raise ValidationError('Password Not Confirmed.')


class SendMessageForm(FlaskForm):
    recipient_email = StringField('Recipient Email', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired()])
    body = StringField('Body')
    submit = SubmitField('Send')

    def validate_recipient_email(self, recipient_email):
        user = User.query.filter_by(email=recipient_email.data).first()
        if user :
            pass
        else:
            raise ValidationError('Recipient not found.')


class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update Profile')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user and current_user.email != email.data:
            raise ValidationError('Email is already in use.')

