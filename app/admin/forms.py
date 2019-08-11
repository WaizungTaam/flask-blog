from flask import session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, \
    TextAreaField
from wtforms.validators import DataRequired, ValidationError

from app.captcha import CaptchaField
from app.user.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    captcha = CaptchaField('Captcha', validators=[DataRequired()])
    submit = SubmitField('Login')

    def validate_captcha(self, captcha):
        if captcha.data.lower() != session['captcha'].lower():
            raise ValidationError('Wrong captcha.')


class SendMailForm(FlaskForm):
    sender = SelectField('From', validators=[DataRequired()], coerce=int)
    receiver = StringField('To', validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content')
    submit = SubmitField('Send')

    def load_senders(self):
        self.sender.choices = [(u.id, u.username) for u in User.official_users()]
