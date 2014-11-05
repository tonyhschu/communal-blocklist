from communalblocklist import app
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_dance.models import OAuthConsumerMixin
from flask.ext.login import LoginManager, UserMixin

db = SQLAlchemy(app)

topics_users = db.Table('topics_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
        db.Column('topic_id', db.Integer(), db.ForeignKey('topic.id')))

topics_blocks = db.Table('topics_blocks',
        db.Column('blocks_id', db.Integer(), db.ForeignKey('block.id')),
        db.Column('topic_id', db.Integer(), db.ForeignKey('topic.id')))

users_blocked = db.Table('users_blocked',
        db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
        db.Column('block_id', db.Integer(), db.ForeignKey('block.id')))

users_exception = db.Table('users_exception',
        db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
        db.Column('block_id', db.Integer(), db.ForeignKey('block.id')))

class Topic(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
    blocks = db.relationship('Block', secondary=topics_blocks,
                            backref=db.backref('block', lazy='dynamic'))

    def __repr__(self):
        return '<Topic %r>' % self.name

    def toJSON(self):
        return {
            "name": self.name,
            "size": len(self.blocks)
        }

class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    t_id = db.Column(db.Integer)
    email = db.Column(db.String(255), unique=True)
    screen_name = db.Column(db.String(15), nullable=False)

    topics = db.relationship('Topic', secondary=topics_users,
                            backref=db.backref('users', lazy='dynamic'))

    blocked = db.relationship('Block', secondary=users_blocked,
                            backref=db.backref('users_blocked', lazy='dynamic'))

    exception = db.relationship('Block', secondary=users_exception,
                            backref=db.backref('users_exception', lazy='dynamic'))

    def __repr__(self):
        return '<User %r>' % self.screen_name

    def toJSON(self):
        return self.screen_name

class Block(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    t_id = db.Column(db.Integer, unique=True)
    screen_name = db.Column(db.String(15), nullable=False)
    topics = db.relationship('Topic', secondary=topics_blocks,
                            backref=db.backref('topic', lazy='dynamic'))
    first_blocked = db.Column(db.DateTime, default=datetime.utcnow)
    by_user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    by_user = db.relationship(User)

    def toJSON(self):
        def getTopicJSON(topic):
            return {
              "id": topic.id,
              "name": topic.name
            }


        return {
            "user_id": self.t_id,
            "topics": map(getTopicJSON, self.topics)
        }

class OAuth(db.Model, OAuthConsumerMixin):
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User)

    def __repr__(self):
        return '<OAuth %r>' % self.user_id


def get_or_create(model, **kwargs):
    instance = db.session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        instance = model(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance, True