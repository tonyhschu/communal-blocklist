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
        twitter_blueprint.set_token_storage_sqlalchemy(OAuth, db.session, user=current_user)
        db.session.commit()

        login_user(user_record)

        return "welcome"
    else:
        login_user(user_record)
        return "You are back, @{screen_name}!".format(screen_name=current_user.screenname)

        '''
        oauth_record = OAuth.query.filter_by(user_id=user_record.id).first()
        if oauth_record is None:
            twitter_blueprint.set_token_storage_sqlalchemy(OAuth, db.session, user=current_user)
            return "NOPE"
        else:
            return oauth_record
            #return "You are back, @{screen_name}!".format(screen_name=user_record.screenname)
        '''

@app.route("/thing")
def thing():
    '''
    oauth_record = OAuth.query.filter_by(user_id=current_user.id).first()
    app.logger.debug(oauth_record)
    return oauth_record
    '''
    '''
    app.logger.debug(twitter_blueprint.token)
    return twitter_blueprint.token
    '''

    twitter_blueprint.set_token_storage_sqlalchemy(OAuth, db.session)

    '''
    db.session.commit()
    oauth_record = OAuth.query.filter_by(user_id=current_user.id).first()
    app.logger.debug(oauth_record)
    '''
    return "bah"

@app.route("/admin")
def admin():
    app.logger.debug(current_user)

    if current_user.is_authenticated():
        return "True"
    else:
        return "False"

    '''
    user = User(screenname=screenname)
    db.session.add(user)
    db.session.commit()

    login_user(current_user)

    twitter_blueprint.set_token_storage_sqlalchemy(twitter, db.session, user=current_user)
    '''
    #return screenname
    '''
    twitter_blueprint.set_token_storage_sqlalchemy(twitter, db.session, user=current_user)

    return user
    '''

