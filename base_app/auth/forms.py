from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, \
                    validators, ValidationError

from base_app.auth.models import User

class LoginForm(FlaskForm):
    """ Define the Login Form """
    email = StringField('Email', [validators.Email(),
            validators.DataRequired(message='Forgot to enter email address?')])
    password = PasswordField('Password', [
            validators.DataRequired(message='Please supply a password.')])
    remember_me = BooleanField('Keep me logged in')

class RegisterForm(FlaskForm):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email is already in use.')

    def validate_name(self, field):
        if User.query.filter_by(name=field.data).first():
            raise ValidationError('Name is already in use.')


class ResetPasswordForm(FlaskForm):
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Unknown email address.')


