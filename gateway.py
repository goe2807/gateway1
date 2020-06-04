from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler


app = Flask(__name__)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

app.config.from_pyfile('config.py')
db = SQLAlchemy(app)

from views import *

if __name__ == '__main__':
    app.run(use_reloader=False)
