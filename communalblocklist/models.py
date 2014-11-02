from communalblocklist import app
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_dance.models import OAuthConsumerMixin
from flask.ext.login import LoginManager, UserMixin

db = SQLAlchemy(app)

topics_users = db.Table('topics_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
        db.Column('topic_id', db.Integer(), db.ForeignKey('topic.id')))

class Topic(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

topics_blocks = db.Table('topics_blocks',
        db.Column('blocks_id', db.Integer(), db.ForeignKey('block.id')),
        db.Column('topic_id', db.Integer(), db.ForeignKey('topic.id')))

class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    t_id = db.Column(db.Integer)
    email = db.Column(db.String(255), unique=True)
    topics = db.relationship('Topic', secondary=topics_users,
                            backref=db.backref('users', lazy='dynamic'))
    screen_name = db.Column(db.String(15), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.screen_name

class Block(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    t_id = db.Column(db.Integer, unique=True)
    topics = db.relationship('Topic', secondary=topics_blocks,
                            backref=db.backref('topic', lazy='dynamic'))
    first_blocked = db.Column(db.DateTime, default=datetime.utcnow)
    by_user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    by_user = db.relationship(User)

class OAuth(db.Model, OAuthConsumerMixin):
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User)

    def __repr__(self):
        return '<OAuth %r>' % self.user_id