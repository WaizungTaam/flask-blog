from heapq import heappush, heappushpop, nlargest
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from app import db
from app.recommend.models import RelatedPost


def calc_post_similarity(post1, post2):
    s1, s2 = set(post1.tags), set(post2.tags)
    return 0 if len(s1 | s2) == 0 else len(s1 & s2) / len(s1 | s2)

def _heappush_with_limit(heap, item, limit=10):
    if len(heap) < limit:
        heappush(heap, item)
    else:
        heappushpop(heap, item)

def set_related_posts(new_post, limit=10):
    from app.post.models import Post
    from sqlalchemy import func
    heap = []
    for post in Post.query.all():
        if post == new_post:
            continue
        score = calc_post_similarity(new_post, post)
        '''
        if score == 0:
            continue
        '''
        if RelatedPost.query.filter_by(target=post.id).count() < limit:
            r = RelatedPost(target=post.id, related=new_post.id, score=score)
            db.session.add(r)
            continue
        lowest = db.session.query(RelatedPost).filter(
            RelatedPost.target == post.id,
            RelatedPost.score == db.session.query(
                func.min(RelatedPost.score)).filter(
                RelatedPost.target == post.id)).first()
        if score > lowest.score:
            db.session.delete(lowest)
            r = RelatedPost(target=post.id, related=new_post.id, score=score)
            db.session.add(r)
        r = RelatedPost(target=new_post.id, related=post.id, score=score)
        _heappush_with_limit(heap, r, limit)
    db.session.add_all(heap)

def build(limit=10):
    from app.post.models import Post
    for post1 in Post.query.all():
        heap = []
        for post2 in Post.query.all():
            score = calc_post_similarity(post1, post2)
            r = RelatedPost(target=post1.id, related=post2.id, score=score)
            _heappush_with_limit(heap, r, limit)
        db.session.add_all(heap)
    db.session.commit()


def _make_doc(post, title_weight=5):
    from app.post.utils import html2text
    return (post.title + ' ') * title_weight + html2text(post.content)

def build_tfidf(limit=10):
    from app.post.models import Post
    db.session.query(RelatedPost).delete()
    tfidf = TfidfVectorizer(stop_words='english')
    posts, docs = zip(*[(p.id, _make_doc(p)) for p in Post.query.all()])
    # TODO: _make_doc is the most time-costing part.
    #       Consider replace `abstract` with `text` in Post.
    matrix = tfidf.fit_transform(docs)
    scores = linear_kernel(matrix, matrix)
    objs = []
    for i, target in enumerate(posts):
        others = [j for j in range(len(posts)) if j != i]
        for j in nlargest(limit, others, key=lambda j: scores[i][j]):
            r = RelatedPost(target=target, related=posts[j],
                score=float(scores[i][j]))
            objs.append(r)
    db.session.bulk_save_objects(objs)
    db.session.commit()
