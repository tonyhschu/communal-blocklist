import os
from flask import Flask, redirect, url_for
from flask.ext.sqlalchemy import SQLAlchemy

from flask_dance.contrib.twitter import make_twitter_blueprint, twitter
from flask_dance.models import OAuthConsumerMixin

app = Flask(__name__)
app.config.from_pyfile('config.py')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL","postgresql://localhost/communal_blocklist")

twitter_blueprint = make_twitter_blueprint(
    api_key=os.environ['TWITTER_KEY'],
    api_secret=os.environ['TWITTER_SECRET'],
    redirect_to="next",
)
app.register_blueprint(twitter_blueprint, url_prefix="/login")

db = SQLAlchemy(app)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # ... other columns as needed

class OAuth(db.Model, OAuthConsumerMixin):
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User)

@app.route('/')
def hello():
    # return "hello world"

    if not twitter.authorized:
        return redirect(url_for("twitter.login"))

    resp = twitter.get("/user")
    assert resp.ok
    return "You are @{login} on Twitter".format(login=resp.json()["login"])

'''
@app.route('/next')
def next():
    return 'Next'
'''