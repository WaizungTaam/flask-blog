from datetime import datetime
from app import db
from app.search.models import SearchableMixin


class Post(db.Model, SearchableMixin):
    __tablename__ = 'posts'
    __searchable__ = ['title', 'content']

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    content = db.Column(db.Text())
    content_type = db.Column(db.String(10))
    abstract = db.Column(db.String(100))
    ctime = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    mtime = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic',
        order_by='Comment.time.asc()')
    tags = db.relationship(
        'Tag',
        secondary='post_tags',
        primaryjoin='Post.id == post_tags.c.post_id',
        secondaryjoin='post_tags.c.tag_id == Tag.id',
        backref=db.backref('posts', lazy='dynamic'),
        lazy='dynamic'
    )
    read = db.Column(db.Integer, index=True, default=0)


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text())
    time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))


class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), index=True, unique=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))


post_tags = db.Table(
    'post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id')),
)
