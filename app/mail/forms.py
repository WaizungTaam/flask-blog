from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, ValidationError

from app.user.models import User


class MailForm(FlaskForm):
    receiver = StringField('To', validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content')
    submit = SubmitField('Send')

    def validate_receiver(self, receiver):
        user = User.query.filter_by(username=receiver.data).first()
        if user is None:
            raise ValidationError('Invalid receiver.')
