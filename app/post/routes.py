from datetime import datetime

from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import current_user, login_required

from app import db
from app.post import bp
from app.post.models import Post, Comment
from app.post.forms import NewPostForm, EditPostForm, CommentForm


@bp.route('/posts', methods=['GET'])
def list_posts():
    posts = Post.query.order_by(Post.mtime.desc()).all()
    return render_template('post/list_posts.html', title='List Posts',
        posts=posts)

@bp.route('/posts/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = NewPostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            content=form.content.data,
            author=current_user
        )
        db.session.add(post)
        db.session.commit()
        flash('New post submitted.')
        return redirect(url_for('post.show_post', id=post.id))
    return render_template('post/new_post.html', title='New Post', form=form)

@bp.route('/posts/<int:id>', methods=['GET', 'POST'])
def show_post(id):
    post = Post.query.get_or_404(id)
    if not current_user.is_authenticated:
        return render_template('post/show_post.html',
            title=post.title, post=post)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            content=form.content.data,
            author=current_user,
            post=post
        )
        db.session.add(post)
        db.session.commit()
        flash('Comment posted.')
        return redirect(url_for('post.show_post', id=post.id))
    return render_template('post/show_post.html',
        title=post.title, post=post, form=form)

@bp.route('/posts/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author:
        abort(403)
    form = EditPostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.mtime = datetime.utcnow()
        db.session.commit()
        flash('Post updated.')
        return redirect(url_for('post.show_post', id=id))
    form.title.data = post.title
    form.content.data = post.content
    return render_template('post/edit_post.html', title='Edit Post', form=form)

@bp.route('/posts/<int:id>/delete', methods=['GET'])
@login_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted.')
    return redirect(url_for('user.show_user', id=current_user.id))
