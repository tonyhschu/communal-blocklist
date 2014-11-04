from communalblocklist import app
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
def add_together(a, b):
    return a + b

'''
>>> import communalblocklist.tasks
>>> communalblocklist.tasks.add_together.delay(1, 2)
'''