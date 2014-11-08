from communalblocklist import app
from communalblocklist.utils import computeSetsForUser, blockForUser
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

    if resp.status_code is "200":
        app.logger.debug("yay")

        user.blocked.append(block)
        db.session.commit()
        db.session.close()
    else:
        app.logger.debug("booo")

@celery.task()
def syncUser(user_id):
    user = User.query.filter_by(id = user_id).first()
    sets = computeSetsForUser(user)

    for t_id in sets["to_sync"]:
        blockIDForUserID.delay(t_id, user_id)

    db.session.close()

@celery.task()
def queueSync():
    for u in db.session.query(User):
        syncUser.delay(u.id)

    db.session.close()