def calc_post_similarity(post1, post2):
    s1, s2 = set(post1.tags), set(post2.tags)
    return 0 if len(s1 | s2) == 0 else len(s1 & s2) / len(s1 | s2)

def set_related_posts(new_post, limit=10):
    from app.post.models import Post
    from app.recommend.models import RelatedPost
    from app import db
    from sqlalchemy import func
    from heapq import heappush, heappushpop
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
        if len(heap) < limit:
            heappush(heap, r)
        else:
            heappushpop(heap, r)
    for r in heap:
        db.session.add(r)

def build():
    from app.post.models import Post
    from app.recommend.models import RelatedPost
    from app import db
    for post1 in Post.query.all():
        for post2 in Post.query.all():
            score = calc_post_similarity(post1, post2)
            r = RelatedPost(target=post1.id, related=post2.id, score=score)
            db.session.add(r)
    db.session.commit()
