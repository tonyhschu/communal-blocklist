from communalblocklist import app
from flask import redirect, url_for
from flask_dance.contrib.twitter import twitter

@app.route("/")
def index():
    if not twitter.authorized:
        return redirect(url_for("twitter.login"))

    resp = twitter.get("account/verify_credentials.json")
    assert resp.ok

    return "You are @{screen_name} on Twitter".format(screen_name=resp.json()["screen_name"])