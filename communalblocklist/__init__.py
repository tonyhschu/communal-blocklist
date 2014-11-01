import os
from flask import Flask
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter
from flask.ext.security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required

app = Flask(__name__)
app.config['DEBUG'] = os.environ['DEBUG']
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['DATABASE_URL'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_DATABASE_URI'] = app.config['DATABASE_URL']

app.debug = True

# os.environ variable are either in .env (locally), or set via heroku config:set TWITTER_KEY=XXXXXXX
twitter_blueprint = make_twitter_blueprint(
    api_key=os.environ['TWITTER_KEY'],
    api_secret=os.environ['TWITTER_SECRET'],
    redirect_url=os.environ['REDIRECT_URL'],
)
app.register_blueprint(twitter_blueprint, url_prefix="/login")

import communalblocklist.views
import communalblocklist.api
import communalblocklist.models