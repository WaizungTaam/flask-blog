from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login


followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('following_id', db.Integer, db.ForeignKey('users.id'))
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


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
