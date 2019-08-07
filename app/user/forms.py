from flask import session
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SelectField, \
    DateField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, Email, \
    Optional, ValidationError

from app.user.models import User
from app.captcha import CaptchaField


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    captcha = CaptchaField('Captcha', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

    def validate_captcha(self, captcha):
        if captcha.data.lower() != session['captcha'].lower():
            raise ValidationError('Wrong captcha.')


class SignupForm(FlaskForm):
    username = StringField('Username',
        validators=[DataRequired(), Length(min=1, max=50)])
    password = PasswordField('Password',
        validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirm Password',
        validators=[DataRequired(), EqualTo('password')])
    captcha = CaptchaField('Captcha', validators=[DataRequired()])
    submit = SubmitField('Signup')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username already exists.')

    def validate_captcha(self, captcha):
        if captcha.data.lower() != session['captcha'].lower():
            raise ValidationError('Wrong captcha.')


class ProfileForm(FlaskForm):
    name = StringField('Name', validators=[Optional()])
    gender = SelectField('Gender',
        choices=[
            ('', ''),
            ('Male', 'Male'),
            ('Female', 'Female'),
            ('Others', 'Others')
        ],
        validators=[Optional()]
    )
    birthday = DateField('Birthday', validators=[Optional()])
    phone = StringField('Phone', validators=[Optional()])
    email = StringField('Email', validators=[Optional(), Email()])
    location = StringField('Location', validators=[Optional()])
    about = TextAreaField('About', validators=[Optional()])
    avatar = FileField('Avatar',
        validators=[Optional(), FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Submit')

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('New Password',
        validators=[DataRequired(), Length(min=6)])
    new_password2 = PasswordField('Confirm New Password',
        validators=[DataRequired(), EqualTo('new_password',
            'Must be equal to New Password.')])
    sumit = SubmitField('Update')
