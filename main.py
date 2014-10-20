import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL","postgresql://localhost/communal_blocklist")

db = SQLAlchemy(app)

@app.route('/')
def hello():
    return 'Hello World!'

