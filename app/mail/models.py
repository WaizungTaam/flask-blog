from datetime import datetime
from app import db


class Mail(db.Model):
    __tablename__ = 'mails'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    content = db.Column(db.Text())
    time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    read = db.Column(db.Boolean)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'))
