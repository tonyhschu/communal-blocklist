from communalblocklist import app, os
from communalblocklist.models import Block, Topic, User, OAuth, db, get_or_create
from requests_oauthlib import OAuth1Session
from flask import request

def getTopicID(topic):
    return topic.id

def getTwitterIDs(block):
    return block.t_id

def getTwitterSession(user):
    oauthRecord = OAuth.query.filter_by(user_id = user.id).first()
    oauthToken = oauthRecord.token

    return OAuth1Session(os.environ['TWITTER_KEY'], client_secret=os.environ['TWITTER_SECRET'], resource_owner_key=oauthToken['oauth_token'], resource_owner_secret=oauthToken['oauth_token_secret'])

def blockForUser(block, user):
    twitter = getTwitterSession(user)

    payload = {'user_id': block.t_id, 'include_entities': False, 'skip_status': False}
    return twitter.post("https://api.twitter.com/1.1/blocks/create.json", data=payload)

def computeSetsForUser(user):
    subscribed_topics = user.topics

    twitter = getTwitterSession(user)

    # Getting the current list of blocks for this user
    resp = twitter.get("https://api.twitter.com/1.1/blocks/ids.json")
    current_blocks = resp.json()

    current_set = set(current_blocks["ids"])

    # Get all users covered by subscribed topics
    subscribed_topic_ids = map(getTopicID, subscribed_topics)

    if subscribed_topic_ids:
        all_blocks = Block.query.filter(Block.topics.any(Topic.id.in_(subscribed_topic_ids))).all()
        all_set = set(map(getTwitterIDs, all_blocks))
    else:
        all_set = set()

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