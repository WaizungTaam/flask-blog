from flask import current_app, render_template, request, url_for, redirect, g
from app.search import bp

@bp.route('/search')
def search():
    if not g.search_form.validate():
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    from app.post.models import Post
    posts, total = Post.search(g.search_form.q.data, page,
        current_app.config['POSTS_PER_PAGE'])
    next_url = url_for('search.search',
        q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('search.search',
        q=g.search_form.q.data, page=page - 1) if page > 1 else None
    return render_template(
        'search/search.html', title='Search', posts=posts,
        page=page, next_url=next_url, prev_url=prev_url)
