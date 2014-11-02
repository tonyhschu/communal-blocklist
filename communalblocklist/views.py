from communalblocklist import app, twitter_blueprint
from communalblocklist.models import db, User, OAuth
from flask import redirect, url_for
from flask_dance.contrib.twitter import twitter
from flask.ext.login import login_user, logout_user, current_user, login_required

@app.route("/")
def index():
    if current_user.is_authenticated():
        return "You are back, @{screen_name}!".format(screen_name=current_user.screen_name)
    else:
        return "Welcome to communal blocklist <a href=\"/auth\">Login</a>"

@app.route("/auth")
def auth():
    if not twitter.authorized:
        return redirect(url_for("twitter.login"))

    resp = twitter.get("account/verify_credentials.json")
    rjson = resp.json()

    t_id = rjson["id"]
    screen_name = rjson["screen_name"]

    user_record = User.query.filter_by(t_id=t_id).first()

    if user_record is None:
        user_record = User(t_id = t_id, screen_name=screen_name)

        twitter_blueprint.set_token_storage_sqlalchemy(OAuth, db.session, user=user_record)

        db.session.add(user_record)
        db.session.commit()

    login_user(user_record)

    return redirect("/")