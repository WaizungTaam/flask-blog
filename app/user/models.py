from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.String(128))

    def __init__(self, username, password):
        self.username = username
        self.password = generate_password_hash(password)

    def verify(username, password):
        user = User.query.filter_by(username=username).first()
        if user is not None and check_password_hash(user.password, password):
            return user
        return None


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
