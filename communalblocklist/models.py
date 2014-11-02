from communalblocklist import app
from flask_sqlalchemy import SQLAlchemy
from flask_dance.models import OAuthConsumerMixin
from flask.ext.login import LoginManager, UserMixin

db = SQLAlchemy(app)

roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    screenname = db.Column(db.String(15), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.screenname

class OAuth(db.Model, OAuthConsumerMixin):
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User)

    def __repr__(self):
        return '<OAuth %r>' % self.user_id