from communalblocklist import app
from communalblocklist.models import Block, Topic, User, db, get_or_create
from flask import request
from flask_dance.contrib.twitter import twitter
from flask.ext.login import current_user

def getTopicID(topic):
    return topic.id

def getTwitterIDs(block):
    return block.t_id

def computeSetsForCurrentUser():
    subscribed_topics = current_user.topics

    # Getting the current list of blocks for this user
    resp = twitter.get("blocks/ids.json")
    current_blocks = resp.json()

    app.logger.debug(current_blocks)

    current_set = set(current_blocks["ids"])

    # Get all users covered by subscribed topics
    subscribed_topic_ids = map(getTopicID, subscribed_topics)

    all_blocks = Block.query.filter(Block.topics.any(Topic.id.in_(subscribed_topic_ids))).all()

    all_set = set(map(getTwitterIDs, all_blocks))

    # Get all recorded blocks
    recorded_blocks = current_user.blocked
    recorded_set = set(map(getTwitterIDs, recorded_blocks))

    # Get all exceptions
    block_exceptions = current_user.exception
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