from communalblocklist import app
from flask_dance.contrib.twitter import twitter
from flask.ext import restful

api = restful.Api(app)

class User(restful.Resource):
    def get(self):
        return {'hello': 'world'}

api.add_resource(User, '/user')