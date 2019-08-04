from os.path import splitext, join
from uuid import uuid4

from flask import render_template, url_for, flash, redirect, abort, \
    current_app, send_from_directory, request
from flask_login import current_user, login_user, logout_user, login_required

from app import db
from app.user import bp
from app.user.models import User, Profile
from app.user.forms import LoginForm, SignupForm, ProfileForm


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user.show_user', id=current_user.id))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.verify(form.username.data, form.password.data)
        if not user:
            flash('Invalid username or password.')
            return redirect(url_for('user.login'))
        login_user(user, remember=form.remember_me.data)
        '''
        return redirect(
            request.args.get('next') or \
            request.referrer or \
            url_for('user.show_user', id=user.id))
        '''
        # TODO: The referrer for POST is itself, which comes from GET.
        #       A better way to trace history is required.
        return redirect(
            request.args.get('next') or \
            url_for('user.show_user', id=user.id))
    return render_template('user/login.html', title='Login', form=form)

@bp.route('/logout', methods=['GET'])
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash('Successfully logout.')
    return redirect(url_for('user.login'))

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('user.show_user', id=current_user.id))
    form = SignupForm()
    if form.validate_on_submit():
        user = User(form.username.data, form.password.data)
        profile = Profile(user=user)
        db.session.add(user)
        db.session.add(profile)
        db.session.commit()
        flash('Congratulations! You are now a registered user.')
        return redirect(url_for('user.login'))
    return render_template('user/signup.html', title='Signup', form=form)

@bp.route('/users/<int:id>', methods=['GET'])
def show_user(id):
    user = User.query.get(id)
    if not user:
        abort(404)
    return render_template('user/show_user.html',
        title=user.username, user=user)

@bp.route('/users/<int:id>/follow')
@login_required
def follow(id):
    user = User.query.get(id)
    if not user:
        flash('User not found.')
    elif user == current_user:
        flash('Cannot follow yourself.')
    else:
        current_user.follow(user)
        db.session.commit()
        flash('Followed user {}.'.format(user.username))
    return redirect(url_for('user.show_user', id=id))

@bp.route('/users/<int:id>/unfollow')
@login_required
def unfollow(id):
    user = User.query.get(id)
    if not user:
        flash('User not found.')
    elif user == current_user:
        flash('Cannot unfollow yourself.')
    else:
        current_user.unfollow(user)
        db.session.commit()
        flash('Unfollowed user {}'.format(user.username))
    return redirect(url_for('user.show_user', id=id))


@bp.route('/users/<int:id>/profile', methods=['GET'])
def show_profile(id):
    user = User.query.get_or_404(id)
    profile = user.profile
    return render_template('user/show_profile.html', profile=profile)

@bp.route('/users/<int:id>/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile(id):
    user = User.query.get_or_404(id)
    if current_user != user:
        abort(403)
    profile = user.profile
    form = ProfileForm()
    if form.validate_on_submit():
        profile.name = form.name.data or None
        profile.gender = form.gender.data or None
        profile.birthday = form.birthday.data or None
        profile.phone = form.phone.data or None
        profile.email = form.email.data or None
        profile.location = form.location.data or None
        profile.about = form.about.data or None
        file = form.avatar.data
        if file:
            fname = uuid4().hex + splitext(file.filename)[1]
            # TODO: Preprocess image
            file.save(join(
                current_app.config['UPLOAD_FOLDER'], 'avatars', fname))
            profile.avatar = url_for('user.get_avatar', fname=fname)
        db.session.commit()
        flash('Profile updated.')
        return redirect(url_for('user.show_profile', id=user.id))
    form.name.data = profile.name or ''
    form.gender.data = profile.gender or ''
    form.birthday.data = profile.birthday or ''
    form.phone.data = profile.phone or ''
    form.email.data = profile.email or ''
    form.location.data = profile.location or ''
    form.about.data = profile.about or ''
    return render_template('user/edit_profile.html', form=form)

@bp.route('/avatars/<fname>')
def get_avatar(fname):
    return send_from_directory(
        join(current_app.config['UPLOAD_FOLDER'], 'avatars'), fname)

@bp.route('/users/<int:id>/stars', methods=['GET'])
def show_stars(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    posts = user.stars.paginate(
        page, current_app.config['POSTS_PER_PAGE'])
    prev_url = url_for('user.show_stars', page=posts.prev_num) \
        if posts.has_prev else None
    next_url = url_for('post.show_stars', page=posts.next_num) \
        if posts.has_next else None
    return render_template('/user/show_stars.html',
        title='Stars', posts=posts.items, page=page,
        prev_url=prev_url, next_url=next_url)
