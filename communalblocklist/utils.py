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

def getProfiles(t_id_list, user):
    twitter = getTwitterSession(user)

    IDs = ",".join(map(str,t_id_list))

    payload = {'user_id' : IDs, 'include_entities' : False}

    return twitter.post("https://api.twitter.com/1.1/users/lookup.json", data=payload)

def blockForUser(block, user):
    twitter = getTwitterSession(user)

    payload = {'user_id': block.t_id, 'include_entities': False, 'skip_status': False}
    return twitter.post("https://api.twitter.com/1.1/blocks/create.json", data=payload)

def computeSetsForUser(user):
    subscribed_topics = user.topics

    twitter = getTwitterSession(user)

    # Getting the current list of blocks for this user
    resp = twitter.get("https://api.twitter.com/1.1/blocks/ids.json?stringify_ids=true")
    current_blocks = resp.json()

    current_set = set(current_blocks["ids"])

    app.logger.debug(current_set)

    # Get all users covered by subscribed topics
    subscribed_topic_ids = map(getTopicID, subscribed_topics)

    if subscribed_topic_ids:
        all_blocks = Block.query.filter(Block.topics.any(Topic.id.in_(subscribed_topic_ids))).all()
        all_set = set(map(getTwitterIDs, all_blocks))
    else:
        all_set = set()

    # Get all recorded blocks
    recorded_set = set(map(getTwitterIDs, user.blocked))

    # Get all exceptions
    exception_set = set(map(getTwitterIDs, user.exception))

    # Get all uncategorized
    uncategorized_set = set(map(getTwitterIDs, user.uncategorized))

    # Get all private
    private_set = set(map(getTwitterIDs, user.private))

    # Compute targets
    target_set = all_set.difference(exception_set)

    # Compute new set
    new_set = current_set.difference(target_set, recorded_set, uncategorized_set, private_set)

    # Compute set of syncs required
    sync_set = target_set.difference(current_set, exception_set)

    # Compute convience total set
    union_set = all_set.union(current_set, exception_set)

    return {
        "target" : list(target_set),
        "exception" : list(exception_set),
        "on_twitter" : list(current_set),
        "recorded" : list(recorded_set),
        "new" : list(new_set),
        "uncategorized" : list(uncategorized_set),
        "private" : list(private_set),
        "to_sync" : list(sync_set),
        "union" : list(union_set)
    }