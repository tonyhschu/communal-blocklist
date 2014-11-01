from communalblocklist import app
from flask_dance.contrib.twitter import twitter
from flask.ext import restful

api = restful.Api(app)

class CurrentUser(restful.Resource):
    def get(self):
        if not twitter.authorized:
            return {
                'status': 'redirect',
                'redirect': 'login'
            }

        resp = twitter.get("account/verify_credentials.json")
        assert resp.ok

        return resp.json()

api.add_resource(CurrentUser, '/api/current_user')