from werkzeug.security import generate_password_hash, check_password_hash

from app import db


class Admin(db.Model):
    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), index=True, unique=True)
    password = db.Column(db.String(512))

    # TODO: Defining a __init__ may cause problem. See user.User
    def __init__(self, username, password):
        self.username = username
        self.password = generate_password_hash(password)

    def verify(username, password):
        admin = Admin.query.filter_by(username=username).first()
        if admin is not None and check_password_hash(admin.password, password):
            return admin
        return None
