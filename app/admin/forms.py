from flask_wtf import FlaskForm
from flask_wtf.recaptcha import Recaptcha, RecaptchaField
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    recaptcha = RecaptchaField(validators=[Recaptcha('Verification Failed')])
    submit = SubmitField('Login')
