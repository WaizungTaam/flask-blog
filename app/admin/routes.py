from flask import request, render_template, session, redirect, url_for, flash
from sqlalchemy import text

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

@bp.route('/admin/login', methods=['GET', 'POST'])
def login():
    if admin_logged_in():
        return redirect(request.referrer or url_for('admin.index'))
    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.verify(form.username.data, form.password.data)
        if not admin:
            flash('Invalid username or password.')
            return redirect(url_for('admin.login'))
        login_admin(admin)
        return redirect(request.referrer or url_for('admin.index'))
    return render_template('admin/login.html', title='Login',
        loggedin=False, form=form)

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
    from app.user.models import User
    action = request.args.get('action')
    if action == 'insert':
        user = User(
            username=request.args.get('username'),
            password=request.args.get('password')
        )
        db.session.add(user)
        # TODO: Maybe should set user.profile
        db.session.commit()
        flash('New user {} inserted.'.format(user.id))
        return redirect(url_for('admin.index',
            action='select', q='id = {}'.format(user.id)))
    elif action == 'update':
        q = text(request.args.get('q', ''))
        query = User.query.filter(q)
        count = 0
        if request.args.get('username'):
            if query.count() == 1:
                user = query.first()
                user.username = request.args.get('username')
                count = 1
        if request.args.get('password'):
            password = request.args.get('password')
            for user in query.all():
                user.set_password(password)
            count = query.count()
        db.session.commit()
        flash('{} users updated.'.format(count))
        return redirect(url_for('admin.index', action='select', q=q))
    elif action == 'delete':
        q = text(request.args.get('q', ''))
        # count = User.query.filter(q).delete(synchronize_session=False)
        # Bulk delete. Cannot cascade.
        users = User.query.filter(q).all()
        for user in users:
            db.session.delete(user)
        db.session.commit()
        flash('{} users deleted.'.format(len(users)))
        return redirect(url_for('admin.index', action='select', q=q))
    else:
        q = text(request.args.get('q', ''))
        page = request.args.get('page', 1)
        users = User.query.filter(q).paginate(page, 20)
        prev_url = url_for('admin.index', page=users.prev_num) \
            if users.has_prev else None
        next_url = url_for('admin.index', page=users.next_num) \
            if users.has_next else None
        return render_template('admin/index.html', users=users.items, q=q,
            page=page, prev_url=prev_url, next_url=next_url)
