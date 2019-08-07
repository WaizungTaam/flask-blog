from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length

from app.post.models import Post


class NewPostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = HiddenField()
    content_type = HiddenField()
    tag = StringField('Tag', validators=[Length(max=50)])
    submit = SubmitField('Post')


class EditPostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = HiddenField()
    content_type = HiddenField()
    tag = StringField('Tag', validators=[Length(max=50)])
    submit = SubmitField('Update')


class CommentForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Comment')
