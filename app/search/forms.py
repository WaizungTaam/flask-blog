from flask import request, g
from flask_wtf import FlaskForm
from wtforms import StringField


class SearchForm(FlaskForm):
    q = StringField('Search')

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)
