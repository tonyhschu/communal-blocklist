import os
from flask import Flask
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter
from flask.ext.login import LoginManager

app = Flask(__name__)
app.config['DEBUG'] = os.environ['DEBUG']
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['DATABASE_URL'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_DATABASE_URI'] = app.config['DATABASE_URL']

app.config['BROKER_URL']=os.environ['REDISGREEN_URL']
app.config['CELERY_RESULT_BACKEND']=os.environ['REDISGREEN_URL']

app.debug = True

# os.environ variable are either in .env (locally), or set via heroku config:set TWITTER_KEY=XXXXXXX
twitter_blueprint = make_twitter_blueprint(
    api_key=os.environ['TWITTER_KEY'],
    api_secret=os.environ['TWITTER_SECRET'],
    redirect_url=os.environ['REDIRECT_URL'],
)
app.register_blueprint(twitter_blueprint, url_prefix="/login")

import communalblocklist.models
from communalblocklist.models import User, Topic, db
import communalblocklist.views
import communalblocklist.api
import communalblocklist.tasks

# Start login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth"

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

