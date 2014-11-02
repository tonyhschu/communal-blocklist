from communalblocklist import app, twitter_blueprint
from communalblocklist.models import db, User, OAuth
from flask import redirect, url_for
from flask_dance.contrib.twitter import twitter
from flask.ext.login import login_user, logout_user, current_user, login_required

@app.route("/")
def index():
    if not twitter.authorized:
        return redirect(url_for("twitter.login"))

    resp = twitter.get("account/verify_credentials.json")
    assert resp.ok

    screenname = resp.json()["screen_name"]

    app.logger.debug(screenname)

    user_record = User.query.filter_by(screenname=screenname).first()

    if user_record is None:
        user_record = User(screenname=screenname)
        db.session.add(user_record)
        db.session.commit()

        login_user(user_record)

        return "welcome"
    else:
        login_user(user_record)
        return "You are back, @{screen_name}!".format(screen_name=current_user.screenname)


@app.route("/admin")
def admin():
    app.logger.debug(current_user)

    if current_user.is_authenticated():
        return "True"
    else:
        return "False"


