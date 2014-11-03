from communalblocklist import app
from communalblocklist.models import Block, Topic, User, db, get_or_create
from flask import request
from flask_dance.contrib.twitter import twitter
from flask.ext.restful import reqparse, abort, Api, Resource
from flask.ext.login import login_user, logout_user, current_user, login_required

api = Api(app)

parser = reqparse.RequestParser()

# Add Blocks
parser.add_argument('user_id', type=int, help='The numeric ID of the twitter user to be blocked.')
parser.add_argument('screen_name', type=str, help='The screen name the twitter user to be blocked.')
parser.add_argument('topics', type=str)
parser.add_argument('topic', type=str)

def toModelJSON(instance):
    return instance.toJSON()

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

class CurrentUserSubscribedTopics(Resource):
    @login_required
    def get(self):
        subscribed_topics = current_user.topics

        return map(toModelJSON, subscribed_topics)

    def post(self):
        args = parser.parse_args()

        topic_name = args["topic"]

        if topic_name is None or not topic_name or topic_name.isspace():
            return {
                "error": "Must provide a topic name to subscribe to."
            }, 404

        topic = Topic.query.filter_by(name=topic_name).first()

        if topic is None:
            return {
                "error": "Must provide an existing topic to subscribe to."
            }
        else:
            if topic in current_user.topics:
                return {
                    "status": "success",
                    "message": "Already subscribed to '{0}'.".format(topic_name),
                    "topics": map(toModelJSON, current_user.topics)
                }
            else:
                current_user.topics.append(topic)
                db.session.commit();

                return {
                    "status": "success",
                    "message": "Successfully subscribed to '{0}'.".format(topic_name),
                    "topics": map(toModelJSON, current_user.topics)
                }

class Blocks(Resource):
    @login_required
    def get(self):
        blocks = Block.query.all()

        return map(toModelJSON, blocks)

    @login_required
    def post(self):
        args = parser.parse_args()

        # Preparing the list of Topics
        topics = []

        # Get or create the All group
        catch_all, catch_all_new = get_or_create(Topic, name="All", description="Catch all blocking group.")
        topics.append(catch_all)

        if args['topics'] is not None:
            tlist = args['topics'].split(",")

            for t in tlist:
                topic_name = t.strip()

                topic, new = get_or_create(Topic, name=topic_name)
                topics.append(topic)

        # Getting the user to be blocked
        '''
        payload = {'screen_name':args['screen_name'],'include_entities':'false'}

        resp = twitter.get("users/lookup.json", params=payload)
        user_details = resp.json()
        '''
        user_details = {"screen_name":"playdangerously", "id":"358545917"}

        block = Block.query.filter_by(t_id=user_details["id"]).first()

        if block is None:
            block = Block(
                t_id=user_details["id"],
                screen_name=user_details["screen_name"],
                by_user_id=current_user.id,
                by_user=current_user,
                topics=topics
            )
            db.session.add(block)
            db.session.commit()
        else:
            # TODO: check if new topics are being added to a current block
            app.logger.debug(block.topics)

        return {
          # "topics": topics,
          "user": user_details
        }

class Topics(Resource):
    @login_required
    def get(self):
        topics = Topic.query.all()

        return map(toModelJSON, topics)

    @login_required
    def post(self):
        args = parser.parse_args()

        topic_name = args["topic"]

        if topic_name is None or not topic_name or topic_name.isspace():
            return {
                "error": "Must provide new topic name."
            }, 400

        topic, new = get_or_create(Topic, name=topic_name)

        if new:
            return topic.toJSON(), 201
        else:
            return topic.toJSON(), 200

api.add_resource(CurrentUser, '/api/current_user')
api.add_resource(CurrentUserSubscribedTopics, '/api/current_user/topics')
api.add_resource(Blocks, '/api/blocks')
api.add_resource(Topics, '/api/topics')