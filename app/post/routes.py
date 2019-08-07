from datetime import datetime

from flask import render_template, redirect, url_for, flash, request, abort, \
    request, current_app, jsonify
from flask_login import current_user, login_required

from app import db
from app.post import bp
from app.post.models import Post, Comment, Tag
from app.post.forms import NewPostForm, EditPostForm, CommentForm
from app.post.utils import make_abstract, parse_tags


@bp.route('/posts', methods=['GET'])
def list_posts():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.mtime.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'])
    prev_url = url_for('post.list_posts', page=posts.prev_num) \
        if posts.has_prev else None
    next_url = url_for('post.list_posts', page=posts.next_num) \
        if posts.has_next else None
    return render_template('post/list_posts.html', title='List Posts',
        posts=posts.items, page=page, prev_url=prev_url, next_url=next_url)

@bp.route('/posts/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = NewPostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            content=form.content.data,
            content_type=form.content_type.data,
            abstract=make_abstract(form.content.data, form.content_type.data),
            author=current_user,
            tags=parse_tags(form.tag.data)
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
        post.abstract = make_abstract(post.content, post.content_type)
        # TODO: Use ref count to remove unused tag.
        post.tags = parse_tags(form.tag.data)
        post.mtime = datetime.utcnow()
        db.session.commit()
        flash('Post updated.')
        return redirect(url_for('post.show_post', id=post.id))
    return render_template('post/edit_post.html', title='Edit Post',
        form=form, post=post, tags=', '.join(tag.name for tag in post.tags))

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

@bp.route('/posts/<int:id>/star', methods=['GET'])
@login_required
def star_post(id):
    post = Post.query.get_or_404(id)
    current_user.star(post)
    db.session.commit()
    flash('Starred.')
    return redirect(url_for('post.show_post', id=id))

@bp.route('/posts/<int:id>/unstar', methods=['GET'])
@login_required
def unstar_post(id):
    post = Post.query.get_or_404(id)
    current_user.unstar(post)
    db.session.commit()
    flash('Unstarred.')
    return redirect(url_for('post.show_post', id=id))

@bp.route('/tags')
def list_tags():
    tags = Tag.query.order_by(Tag.name.asc()).all()
    from string import ascii_uppercase, digits
    c_tags = {c: [] for c in '#-' + ascii_uppercase}
    for tag in tags:
        if tag.name[0] in digits:
            c_tags['#'].append(tag)
        elif tag.name[0].upper() in ascii_uppercase:
            c_tags[tag.name[0].upper()].append(tag)
        else:
            c_tags['-'].append(tag)
    return render_template('post/list_tags.html', c_tags=c_tags)

@bp.route('/tags/<int:id>')
def show_tag(id):
    tag = Tag.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    posts = tag.posts.paginate(page, current_app.config['POSTS_PER_PAGE'])
    prev_url = url_for('post.show_tags', page=posts.prev_num) \
        if posts.has_prev else None
    next_url = url_for('post.show_tags', page=posts.next_num) \
        if posts.has_next else None
    return render_template('post/show_tag.html',
        title='Tag ' + tag.name, tag=tag, posts=posts,
        page=page, prev_url=prev_url, next_url=next_url)
