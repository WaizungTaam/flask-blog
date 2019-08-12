from app import db


class RelatedPost(db.Model):
    __tablename__ = 'related_posts'

    id = db.Column(db.Integer, primary_key=True)
    target = db.Column(db.Integer, db.ForeignKey('posts.id'), index=True)
    related = db.Column(db.Integer, db.ForeignKey('posts.id'))
    score = db.Column(db.Float, default=0)

    def __lt__(self, other):
        return self.score < other.score
