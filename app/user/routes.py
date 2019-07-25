from flask import render_template, url_for, flash, redirect
from flask_login import current_user, login_user, logout_user
from app import db
from app.user import bp
from app.user.models import User
from app.user.forms import LoginForm, SignupForm

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.verify(form.username.data, form.password.data)
        if not user:
            flash('Invalid username or password.')
            return redirect(url_for('user.login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('user/login.html', form=form)

@bp.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash('Successfully logout.')
    return redirect(url_for('user.login'))

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = SignupForm()
    if form.validate_on_submit():
        user = User(form.username.data, form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations! You are now a registered user.')
        return redirect(url_for('user.login'))
    return render_template('user/signup.html', form=form)
