from . import db
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired, BadSignature
from config import Config
from time import time
from passlib.apps import mysql_context as pwd_context


class Task(db.Model):
    __tablename__ = "task"
    id = Column(Integer, primary_key=True)
    text = Column(db.Text, nullable=False)
    done = Column(Boolean, index=True, default=False)
    date = Column(DateTime, default=datetime.now)
    deadline = Column(DateTime, nullable=False)
    author_id = Column(Integer, ForeignKey('users.id'))

    def alter(self, text=None, done=None, deadline=None):
        self.done = [self.done, done][done is not None]
        self.text = [self.text, text][text is not None]
        self.deadline = [self.deadline, deadline][deadline is not None]
        self.date = datetime.now()
        return self


class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(16), unique=True, index=True)
    password_hash = Column(String(64))  # unique似乎是sqlalchemy才有的
    task = db.relationship('Task', backref='author', lazy='dynamic')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=3600):
        s = Serializer(Config.SECRET_KEY, expires_in=expiration)
        return s.dumps({'uid': self.id, 'time': time()})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(Config.SECRET_KEY)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        return User.query.get(data['uid'])
