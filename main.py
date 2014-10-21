import os
from flask import Flask, redirect, url_for
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter

app = Flask(__name__)
app.config.from_pyfile('config.py')
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']

# os.environ variable are either in .env (locally), or set via heroku config:set TWITTER_KEY=XXXXXXX
twitter_blueprint = make_twitter_blueprint(
    api_key=os.environ['TWITTER_KEY'],
    api_secret=os.environ['TWITTER_SECRET'],
    redirect_url=os.environ['REDIRECT_URL'],
)
app.register_blueprint(twitter_blueprint, url_prefix="/login")

@app.route("/")
def index():
    if not twitter.authorized:
        return redirect(url_for("twitter.login"))

    resp = twitter.get("account/verify_credentials.json")
    assert resp.ok

    return "You are @{screen_name} on Twitter".format(screen_name=resp.json()["screen_name"])

if __name__ == "__main__":
    app.run()