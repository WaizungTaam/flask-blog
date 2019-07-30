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
    if request.method == 'POST':
        post = Post(
            title=request.form.get('title'),
            content=request.form.get('content'),
            abstract=make_abstract(request.form.get('content')),
            author=current_user,
            tags=parse_tags(request.form.get('tag'))
        )
        db.session.add(post)
        db.session.commit()
        flash('New post submitted.')
        return jsonify({
            'ok': True,
            'url': url_for('post.show_post', id=post.id)
        })
    form = NewPostForm()
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
        if request.method == 'GET':
            abort(403)
        if request.method == 'POST':
            return jsonify({
                'ok': False,
                'code': 403,
                'url': url_for('error.forbidden_error')
            })
    form = EditPostForm()
    if request.method == 'POST':
        post.title = request.form.get('title')
        post.content = request.form.get('content')
        post.abstract = make_abstract(request.form.get('content'))
        # TODO: Use ref count to remove unused tag.
        post.tags = parse_tags(request.form.get('tag'))
        post.mtime = datetime.utcnow()
        db.session.commit()
        flash('Post updated.')
        return jsonify({
            'ok': True,
            'url': url_for('post.show_post', id=id)
        })
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
    tags = Tag.query.all()
    return render_template('post/list_tags.html', tags=tags)

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
