from communalblocklist import app
from flask import request
from flask_dance.contrib.twitter import twitter
from flask.ext.restful import reqparse, abort, Api, Resource
from flask.ext.login import login_user, logout_user, current_user, login_required

api = Api(app)

class CurrentUser(Resource):
    @login_required
    def get(self):
        resp = twitter.get("account/verify_credentials.json")

        return {
          "id" : current_user.id,
          "t_id" : current_user.t_id,
          "screen_name": current_user.screen_name,
          "twitter": resp.json()
        }

parser = reqparse.RequestParser()

# Add Blocks
parser.add_argument('t_id', type=int, help='Rate cannot be converted')
parser.add_argument('topic', type=str)

class Blocks(Resource):
    @login_required
    def get(self):
        resp = twitter.get("blocks/ids.json")

        return resp.json()

    @login_required
    def post(self):
        args = parser.parse_args()

        return args, 201


api.add_resource(CurrentUser, '/api/current_user')
api.add_resource(Blocks, '/api/blocks')