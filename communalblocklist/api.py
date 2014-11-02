from communalblocklist import app
from flask_dance.contrib.twitter import twitter
from flask.ext import restful
from flask.ext.login import login_user, logout_user, current_user, login_required

api = restful.Api(app)

class CurrentUser(restful.Resource):
    @login_required
    def get(self):
        resp = twitter.get("account/verify_credentials.json")

        return {
          "id" : current_user.id,
          "t_id" : current_user.t_id,
          "screen_name": current_user.screen_name,
          "twitter": resp.json()
        }

api.add_resource(CurrentUser, '/api/current_user')

class Blocks(restful.Resource):
    @login_required
    def get(self):
        resp = twitter.get("blocks/ids.json")

        return resp.json()

api.add_resource(Blocks, '/api/blocks')