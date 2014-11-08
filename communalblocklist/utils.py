from communalblocklist import app, os
from communalblocklist.models import Block, Topic, User, OAuth, db, get_or_create
from requests_oauthlib import OAuth1Session
from flask import request

def getTopicID(topic):
    return topic.id

def getTwitterIDs(block):
    return block.t_id

def computeSetsForUser(user):
    subscribed_topics = user.topics

    oauthRecord = OAuth.query.filter_by(user_id = user.id).first()
    app.logger.debug(oauthRecord)
    oauthToken = oauthRecord.token
    app.logger.debug(oauthToken['oauth_token_secret'])

    twitter = OAuth1Session(os.environ['TWITTER_KEY'], client_secret=os.environ['TWITTER_SECRET'], resource_owner_key=oauthToken['oauth_token'], resource_owner_secret=oauthToken['oauth_token_secret'])

    # Getting the current list of blocks for this user
    resp = twitter.get("https://api.twitter.com/1.1/blocks/ids.json")
    current_blocks = resp.json()

    current_set = set(current_blocks["ids"])

    # Get all users covered by subscribed topics
    subscribed_topic_ids = map(getTopicID, subscribed_topics)

    all_blocks = Block.query.filter(Block.topics.any(Topic.id.in_(subscribed_topic_ids))).all()

    all_set = set(map(getTwitterIDs, all_blocks))

    # Get all recorded blocks
    recorded_blocks = user.blocked
    recorded_set = set(map(getTwitterIDs, recorded_blocks))

    # Get all exceptions
    block_exceptions = user.exception
    exception_set = set(map(getTwitterIDs, recorded_blocks))

    # Compute targets
    target_set = all_set.difference(exception_set)

    # Compute new set
    new_set = current_set.difference(target_set, recorded_set)

    # Compute set of syncs required
    sync_set = target_set.difference(current_set)

    # Compute convience total set
    union_set = all_set.union(current_set, exception_set)

    return {
        "target" : list(target_set),
        "exception" : list(exception_set),
        "on_twitter" : list(current_set),
        "recorded" : list(recorded_set),
        "new" : list(new_set),
        "to_sync" : list(sync_set),
        "union" : list(union_set)
    }