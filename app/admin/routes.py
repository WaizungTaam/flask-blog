from functools import wraps

from flask import request, render_template, session, redirect, url_for, flash

from app.admin import bp
from app.admin.models import Admin
from app.admin.forms import LoginForm
from app import db


def admin_logged_in():
    return 'admin' in session

def login_admin(admin):
    session['admin'] = admin.id

def logout_admin():
    del session['admin']

def admin_login_required(func):
    @wraps(func)
    def wrapper_decorator(*args, **kwargs):
        if not admin_logged_in():
            return redirect(url_for('admin.login'))
        return func(*args, **kwargs)
    return wrapper_decorator


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if admin_logged_in():
        return redirect(request.args.get('next') or url_for('admin.index'))
    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.verify(form.username.data, form.password.data)
        if not admin:
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('admin.login'))
        login_admin(admin)
        return redirect(request.args.get('next') or url_for('admin.index'))
    return render_template('admin/login.html', title='Login', form=form)

@bp.route('/logout', methods=['GET'])
def logout():
    if admin_logged_in():
        logout_admin()
        flash('Successfully logout.')
    return redirect(request.referrer or url_for('admin.login'))

@bp.route('/', methods=['GET'])
def index():
    if not admin_logged_in():
        return redirect(url_for('admin.login'))
    return render_template('admin/index.html')


from wtforms import Field
from wtforms.widgets import TextInput

class RelationsipField(Field):
    widget = TextInput()

    def __init__(self, model, uselist, label=None, validators=None, **kwargs):
        super(RelationsipField, self).__init__(label, validators, **kwargs)
        self.model = model
        self.uselist = uselist

    def process_formdata(self, valuelist):
        if not valuelist:
            return
        try:
            if self.uselist:
                ids = [int(i) for i in valuelist[0].split(',')]
                self.data = [self.model.query.get(i) for i in ids]
                self.data = [i for i in self.data if i is not None]
            else:
                self.data = self.model.query.get(int(valuelist[0]))
        except:
            self.data = [] if self.uselist else None

    def _value(self):
        if not self.data:
            return ''
        if self.uselist:
            return ', '.join(str(item.id) for item in self.data)
        else:
            return str(self.data.id)


class ModelView:
    def __init__(self, model, items_per_page=20):
        self.model = model
        self.items_per_page = items_per_page
        self.name = name = model.__tablename__
        bp.add_url_rule(
            name,
            'list_' + name,
            self.list,
            methods=['GET']
        )
        bp.add_url_rule(
            name + '/insert',
            'insert_' + name[:-1],
            self.insert,
            methods=['GET', 'POST']
        )
        bp.add_url_rule(
            name + '/<int:id>',
            'show_' + name[:-1],
            self.show,
            methods=['GET']
        )
        bp.add_url_rule(
            name + '/<int:id>/update',
            'update_' + name[:-1],
            self.update,
            methods=['GET', 'POST']
        )
        bp.add_url_rule(
            name + '/<int:id>/delete',
            'delete_' + name[:-1],
            self.delete,
            methods=['GET']
        )
        self.list_endpoint = 'admin.list_' + name
        self.insert_endpoint = 'admin.insert_' + name[:-1]
        self.show_endpoint = 'admin.show_' + name[:-1]
        self.update_endpoint = 'admin.update_' + name[:-1]
        self.delete_endpoint = 'admin.delete_' + name[:-1]
        self.InsertForm = self._make_insert_form()
        self.UpdateForm = self._make_update_form()

    @admin_login_required
    def list(self):
        page = request.args.get('page', 1, type=int);
        pagination = self.model.query.paginate(page, self.items_per_page)
        prev_url = url_for(self.list_endpoint, page=pagination.prev_num) \
            if pagination.has_prev else None
        next_url = url_for(self.list_endpoint, page=pagination.next_num) \
            if pagination.has_next else None
        keys = self._list_fields
        rows = [(item.id, self._serialize_values(item, keys)) \
            for item in pagination.items]
        return render_template('admin/model/list.html',
            title=self._cap(self.name), fields=self._list_fields,
            keys=keys, rows=rows, page=page,
            prev_url=prev_url, next_url=next_url,
            insert_endpoint=self.insert_endpoint,
            show_endpoint=self.show_endpoint,
            update_endpoint=self.update_endpoint,
            delete_endpoint=self.delete_endpoint)

    @admin_login_required
    def insert(self):
        form = self.InsertForm()
        if form.validate_on_submit():
            for key in self._insert_fields:
                print(key, getattr(form, key).data)
            item = self.model(**{
                key: self.postprocess(getattr(form, key).data) \
                for key in self._insert_fields})
            db.session.add(item)
            db.session.commit()
            flash('Inserted {}.'.format(item))
            return redirect(url_for(self.show_endpoint, id=item.id))
        return render_template('admin/model/insert.html',
            title='Insert ' + self._cap(self.name[:-1]), form=form)

    @admin_login_required
    def show(self, id):
        item = self.model.query.get_or_404(id)
        keys = self._show_fields
        values = self._serialize_values(item, keys)
        rows = list(zip(keys, values))
        return render_template('admin/model/show.html',
            title='Show ' + self._cap(self.name[:-1]), rows=rows)

    @admin_login_required
    def update(self, id):
        item = self.model.query.get_or_404(id)
        form = self.UpdateForm(obj=item)
        if form.validate_on_submit():
            for field in self._update_fields:
                setattr(item, field,
                    self.postprocess(getattr(form, field).data))
            db.session.commit()
            flash('Updated {}.'.format(item))
            return redirect(url_for(self.show_endpoint, id=item.id))
        return render_template('admin/model/update.html',
            title='Update ' + self._cap(self.name[:-1]), form=form)

    @admin_login_required
    def delete(self, id):
        item = self.model.query.get_or_404(id)
        db.session.delete(item)
        db.session.commit()
        flash('Deleted {}.'.format(item))
        return redirect(url_for(self.list_endpoint))

    def _cap(self, name):
        return name[0].upper() + name[1:]

    @property
    def _list_fields(self):
        columns = [c.name for c in self.model.__mapper__.columns \
            if not c.foreign_keys]
        relationships = [r.key for r in self.model.__mapper__.relationships]
        return columns + relationships

    @property
    def _show_fields(self):
        return self._list_fields

    @property
    def _insert_fields(self):
        return self._list_fields

    @property
    def _update_fields(self):
        return self._insert_fields

    def _get_label(self, name):
        return ' '.join(self._cap(w) for w in name.split('_'))

    def _make_field(self, field, name, optional=True):
        from wtforms.validators import Optional
        validators = [Optional()] if optional else []
        return field(self._get_label(name), validators=validators)

    def _convert_column_to_field(self, column):
        from sqlalchemy.sql.sqltypes import Integer, Boolean, String, Text, \
            Date, DateTime
        from wtforms import IntegerField, BooleanField, StringField, \
            TextAreaField, DateField, DateTimeField
        if type(column.type) is Integer:
            return self._make_field(IntegerField, column.name)
        elif type(column.type) is Boolean:
            return self._make_field(BooleanField, column.name)
        elif type(column.type) is String:
            return self._make_field(StringField, column.name)
        elif type(column.type) is Text:
            return self._make_field(TextAreaField, column.name)
        elif type(column.type) is Date:
            return self._make_field(DateField, column.name)
        elif type(column.type) is DateTime:
            return self._make_field(DateTimeField, column.name)
        else:
            return self._make_field(StringField, column.name)

    def _set_form_fields(self, form):
        from wtforms.validators import Optional
        columns = [c for c in self.model.__mapper__.columns \
            if not c.foreign_keys]
        for column in columns:
            setattr(form, column.name,
                self._convert_column_to_field(column))
        for relationship in self.model.__mapper__.relationships:
            setattr(form, relationship.key,
                RelationsipField(
                    model=relationship.mapper.class_,
                    uselist=relationship.uselist,
                    label=self._get_label(relationship.key),
                    validators=[Optional()]
                ))

    def _make_insert_form(self):
        from flask_wtf import FlaskForm
        from wtforms import SubmitField
        class InsertForm(FlaskForm):
            pass
        self._set_form_fields(InsertForm)
        setattr(InsertForm, 'submit', SubmitField('Insert'))
        return InsertForm

    def _make_update_form(self):
        from flask_wtf import FlaskForm
        from wtforms import SubmitField
        class UpdateForm(FlaskForm):
            pass
        self._set_form_fields(UpdateForm)
        setattr(UpdateForm, 'submit', SubmitField('Update'))
        return UpdateForm

    def _serialize_values(self, item, keys):
        from sqlalchemy.orm.query import Query
        from flask_sqlalchemy.model import Model
        values = []
        for key in keys:
            value = getattr(item, key)
            if issubclass(type(value), Query):
                value = ', '.join(str(i.id) for i in value)
            elif issubclass(type(value), Model):
                value = str(value.id)
            else:
                value = str(value)
            values.append(value)
        return values

    def postprocess(self, value):
        return None if value == '' else value


from app.user.models import User, Profile
from app.mail.models import Mail
from app.post.models import Post, Comment, Tag

users_view = ModelView(User)
profiles_view = ModelView(Profile)
mails_view = ModelView(Mail)
posts_view = ModelView(Post)
comments_view = ModelView(Comment)
tags_view = ModelView(Tag)
