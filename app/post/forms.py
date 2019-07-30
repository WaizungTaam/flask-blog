from flask_wtf import FlaskForm
from flask_wtf.recaptcha import Recaptcha, RecaptchaField
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

from app.post.models import Post


class NewPostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content')
    tag = StringField('Tag', validators=[Length(max=50)])
    recaptcha = RecaptchaField(validators=[Recaptcha('Verification Failed')])
    submit = SubmitField('Post')


class EditPostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content')
    tag = StringField('Tag', validators=[Length(max=50)])
    submit = SubmitField('Update')


class CommentForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired()])
    recaptcha = RecaptchaField(validators=[Recaptcha('Verification Failed')])
    submit = SubmitField('Comment')
