from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
import os

# See: https://realpython.com/blog/python/flask-by-example-part-2-postgres-sqlalchemy-and-alembic/
# foreman run python manage.py db init
# foreman run python manage.py db migrate

from communalblocklist import app
from communalblocklist.models import db

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

print os.environ['DATABASE_URL']

if __name__ == '__main__':
    manager.run()