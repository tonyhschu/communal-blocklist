from communalblocklist import app
from communalblocklist.models import Block, Topic, User, db, get_or_create
from communalblocklist.utils import computeSetsForUser
from flask import request
from flask_dance.contrib.twitter import twitter
from flask.ext.restful import reqparse, abort, Api, Resource
from flask.ext.login import login_user, logout_user, current_user, login_required
from urllib import unquote, urlencode

import sets

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

class CurrentUserSubscribedTopic(Resource):
    @login_required
    def get(self, topic_name):
        topic_name = unquote(topic_name)

        topic = Topic.query.filter_by(name=topic_name).first()

        if topic is None:
            return {
                "error": "The topic '{0}' does not exist.".format(topic_name)
            }, 404
        else:
            if topic in current_user.topics:
                return topic.toJSON()
            else:
                return {
                    "error": "You are not subscribed to '{0}'.".format(topic_name)
                }, 400

    def delete(self, topic_name):
        topic_name = unquote(topic_name)

        topic = Topic.query.filter_by(name=topic_name).first()

        if topic is None:
            return {
                "error": "Must provide an existing topic to unsubscribe from."
            }, 404
        else:
            if topic in current_user.topics:
                current_user.topics.remove(topic)
                db.session.commit();

                return {
                    "status": "success",
                    "message": "Removed subscription to '{0}'.".format(topic_name),
                    "topics": map(toModelJSON, current_user.topics)
                }
            else:
                return {
                    "status": "success",
                    "message": "Not subscribed to to '{0}' anyway.".format(topic_name),
                    "topics": map(toModelJSON, current_user.topics)
                }

class CurrentUserSubscribedTopicsList(Resource):
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

class CurrentUserBlocks(Resource):
    @login_required
    def get(self):
        id_sets = computeSetsForUser(current_user)

        return {
          "target" : id_sets["target"],
          "exception" : id_sets["exception"],
          "on_twitter" : id_sets["on_twitter"],
          "recorded" : id_sets["recorded"],
          "new" : id_sets["new"],
          "to_sync" : id_sets["to_sync"]
        }


class Blocks(Resource):
    @login_required
    def get(self):
        blocks = Block.query.all()

        return map(toModelJSON, blocks)

    @login_required
    def post(self):
        args = parser.parse_args()

        # Validation: was a screen_name provided?
        if args['screen_name'] is None:
            return {
                "error": "Must provide the screen name of twitter user to be blocked."
            }, 400

        # Getting the user to be blocked
        payload = {'screen_name':args['screen_name'],'include_entities':'false'}

        resp = twitter.get("users/lookup.json", params=payload)
        user_details = resp.json()

        if len(user_details) != 1:
            if len(user_details) == 0:
                return {
                    "error": "No user with screen name '{0}' found.".format(args['screen_name'])
                }, 400
            else:
                return {
                    "error": "More than one user with screen name '{0}' found????????".format(args['screen_name'])
                }, 400

        user = user_details[0]

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

        # Checking the user is already in our DB
        block = Block.query.filter_by(t_id=int(user["id_str"])).first()

        if block is None:
            block = Block(
                t_id=user["id_str"],
                screen_name=user["screen_name"],
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
api.add_resource(CurrentUserSubscribedTopicsList, '/api/current_user/topics')
api.add_resource(CurrentUserSubscribedTopic, '/api/current_user/topics/<string:topic_name>')
api.add_resource(CurrentUserBlocks, '/api/current_user/blocks')
api.add_resource(Blocks, '/api/blocks')
api.add_resource(Topics, '/api/topics')