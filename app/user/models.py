from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login


followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('following_id', db.Integer, db.ForeignKey('users.id'))
)

stars = db.Table(
    'stars',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'))
)


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    followings = db.relationship(
        'User',
        secondary=followers,
        primaryjoin=(id == followers.c.follower_id),
        secondaryjoin=(followers.c.following_id == id),
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )
    sent_mails = db.relationship(
        'Mail',
        primaryjoin='User.id == Mail.sender_id',
        backref='sender',
        lazy='dynamic',
        order_by='Mail.time.desc()'
    )
    received_mails = db.relationship(
        'Mail',
        primaryjoin='User.id == Mail.receiver_id',
        backref='receiver',
        lazy='dynamic',
        order_by='Mail.time.desc()'
    )
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    profile = db.relationship('Profile', uselist=False, backref='user')
    stars = db.relationship(
        'Post',
        secondary=stars,
        primaryjoin='User.id == stars.c.user_id',
        secondaryjoin='stars.c.post_id == Post.id',
        backref=db.backref('stars', lazy='dynamic'),
        lazy='dynamic'
    )

    def __init__(self, username, password):
        self.username = username
        self.password = generate_password_hash(password)

    def verify(username, password):
        user = User.query.filter_by(username=username).first()
        if user is not None and check_password_hash(user.password, password):
            return user
        return None

    def is_following(self, user):
        return self.followings.filter(
            followers.c.following_id == user.id).count() > 0

    def follow(self, user):
        if not self.is_following(user):
            self.followings.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followings.remove(user)

    def has_starred(self, post):
        return self.stars.filter(
            stars.c.post_id == post.id).count() > 0

    def star(self, post):
        if not self.has_starred(post):
            self.stars.append(post)

    def unstar(self, post):
        if self.has_starred(post):
            self.stars.remove(post)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Profile(db.Model):
    __tablename__ = 'profiles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    gender = db.Column(db.String(10))
    birthday = db.Column(db.Date())
    phone = db.Column(db.String(20))
    email = db.Column(db.String(80))
    location = db.Column(db.String(80))
    about = db.Column(db.Text())
    avatar = db.Column(db.String(100))
    regtime = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
