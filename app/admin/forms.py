from flask import session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, ValidationError

from app.captcha import CaptchaField


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    captcha = CaptchaField('Captcha', validators=[DataRequired()])
    submit = SubmitField('Login')

    def validate_captcha(self, captcha):
        if captcha.data.lower() != session['captcha'].lower():
            raise ValidationError('Wrong captcha.')


class InsertUserForm(FlaskForm):
    username = StringField('Username',
        validators=[DataRequired(), Length(min=1, max=50)])
    password = StringField('Password',
        validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Insert')


class UpdateUsersForm(FlaskForm):
    q = StringField('Query', validators=[DataRequired()])
    username = StringField('Username',
        validators=[Optional(), Length(min=1, max=50)])
    password = StringField('Password',
        validators=[Optional(), Length(min=6)])
    submit = SubmitField('Update')


class DeleteUsersForm(FlaskForm):
    q = StringField('Query', validators=[DataRequired()])
    submit = SubmitField('Delete')
