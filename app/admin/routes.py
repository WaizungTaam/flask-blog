from flask import request, render_template, session, redirect, url_for, flash
from sqlalchemy import text

from app.admin import bp
from app.admin.models import Admin
from app.admin.forms import LoginForm, InsertUserForm, UpdateUsersForm, \
    DeleteUsersForm
from app import db
from app.user.models import User, Profile


def admin_logged_in():
    return 'admin' in session

def login_admin(admin):
    session['admin'] = admin.id

def logout_admin():
    del session['admin']


@bp.route('/admin/login', methods=['GET', 'POST'])
def login():
    if admin_logged_in():
        return redirect(request.args.get('next') or url_for('admin.index'))
    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.verify(form.username.data, form.password.data)
        if not admin:
            flash('Invalid username or password.')
            return redirect(url_for('admin.login'))
        login_admin(admin)
        return redirect(request.args.get('next') or url_for('admin.index'))
    return render_template('admin/login.html', title='Login', form=form)

@bp.route('/admin/logout', methods=['GET'])
def logout():
    if admin_logged_in():
        logout_admin()
        flash('Successfully logout.')
    return redirect(request.referrer or url_for('admin.login'))

@bp.route('/admin', methods=['GET'])
def index():
    if not admin_logged_in():
        return redirect(url_for('admin.login'))
    return render_template('admin/index.html')


@bp.route('/admin/users', methods=['GET', 'POST'])
def users():
    if not admin_logged_in():
        return redirect(url_for('admin.login'))
    action = request.args.get('a')
    if action == 'select':
        return select_users()
    elif action == 'insert':
        return insert_user()
    elif action == 'update':
        return update_users()
    elif action == 'delete':
        return delete_users()
    else:
        return redirect(url_for('admin.index'))

def _select_users(users_per_page=20):
    query = text(request.args.get('q', ''))
    page = request.args.get('p', 1)
    users = User.query.filter(query).paginate(page, users_per_page)
    prev_url = url_for('admin.users', a='select', p=users.prev_num) \
        if users.has_prev else None
    next_url = url_for('admin.users', a='select', p=users.next_num) \
        if users.has_next else None
    return {
        'users': users.items,
        'query': query,
        'page': page,
        'prev_url': prev_url,
        'next_url': next_url
    }

def select_users():
    return render_template('admin/select_users.html', **_select_users())

def insert_user():
    form = InsertUserForm()
    if form.validate_on_submit():
        user = User(form.username.data, form.password.data)
        profile = Profile(user=user)
        db.session.add(user)
        db.session.add(profile)
        db.session.commit()
        flash('User id = {} inserted.'.format(user.id))
        return redirect(url_for('admin.users',
            a='insert', q='id = {}'.format(user.id)))
    return render_template('admin/insert_user.html',
        form=form, **_select_users(10))

def update_users():
    form = UpdateUsersForm()
    if form.validate_on_submit():
        users = User.query.filter(text(form.q.data)).all()
        count = 0
        if form.username.data:
            for user in users:
                user.username = form.username.data
            count = len(users)
        if form.password.data:
            for user in users:
                user.set_password(form.password.data)
            count = len(users)
        db.session.commit()
        flash('Updated {} users.'.format(count))
        return redirect(url_for('admin.users',
            a='update', q=form.q.data))
    return render_template('admin/update_users.html',
        form=form, **_select_users(10))

def delete_users():
    form = DeleteUsersForm()
    if form.validate_on_submit():
        users = User.query.filter(text(form.q.data)).all()
        for user in users:
            db.session.delete(user)
        db.session.commit()
        flash('Deleted {} users.'.format(len(users)))
        return redirect(url_for('admin.users', a='delete'))
    return render_template('admin/delete_users.html',
        form=form, **_select_users(10))
