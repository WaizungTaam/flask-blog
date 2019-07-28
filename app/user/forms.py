from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_wtf.recaptcha import Recaptcha, RecaptchaField
from wtforms import StringField, PasswordField, BooleanField, SelectField, \
    DateField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, Email, \
    Optional, ValidationError

from app.user.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    recaptcha = RecaptchaField(validators=[Recaptcha('Verification Failed')])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


class SignupForm(FlaskForm):
    username = StringField('Username',
        validators=[DataRequired(), Length(max=50)])
    password = PasswordField('Password',
        validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repeat Password',
        validators=[DataRequired(), EqualTo('password')])
    recaptcha = RecaptchaField(validators=[Recaptcha('Verification Failed')])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Signup')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username already exists.')


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
