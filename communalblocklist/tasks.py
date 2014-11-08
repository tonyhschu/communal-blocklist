from communalblocklist import app
from communalblocklist.utils import computeSetsForUser, blockForUser, getProfiles
from communalblocklist.models import Block, Topic, User, db, get_or_create
from celery import Celery

def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

celery = make_celery(app)

@celery.task()
def blockIDForUserID(t_id, user_id):
    user = User.query.filter_by(id = user_id).first()
    block = Block.query.filter_by(t_id = t_id).first()

    resp = blockForUser(block, user)

    if resp.status_code is 200:
        user.blocked.append(block)
        db.session.commit()
        db.session.close()
    else:
        # couldn't block
        app.logger.error("Unable to block '{0}' for user '{1}. Twitter returned a {2}'".format(block.screen_name, user.screen_name, resp.status_code))

@celery.task()
def addIDsAsUncategorizedForUserID(t_id_set, user_id):
    user = User.query.filter_by(id = user_id).first()

    resp = getProfiles(list(t_id_set), user)

    if resp.status_code is not 200:
        app.logger.error("Unable to retrieve twitter profiles. Twitter returned a {0}'".format(resp.status_code))

    profiles = resp.json()

    for p in profiles:
        app.logger.debug(p["id_str"])

        block = Block.query.filter_by(t_id=p["id_str"]).first()

        if block is None:
            block = Block(
                t_id=p["id_str"],
                screen_name=p["screen_name"]
            )
            db.session.add(block)
            db.session.commit()

        user.uncategorized.append(block)


@celery.task()
def syncUser(user_id):
    user = User.query.filter_by(id = user_id).first()
    sets = computeSetsForUser(user)

    for t_id in sets["to_sync"]:
        blockIDForUserID.delay(t_id, user_id)

    if sets["new"]:
        addIDsAsUncategorizedForUserID.delay(sets["new"], user_id)

    db.session.close()

@celery.task()
def queueSync():
    for u in db.session.query(User):
        syncUser.delay(u.id)

    db.session.close()