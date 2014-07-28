# http://charlesleifer.com/blog/structuring-flask-apps-a-how-to-for-those-coming-from-django/

import os
from flask import Flask
from flask_bootstrap import Bootstrap

# flask-peewee database, but could be SQLAlchemy instead.
from flask_peewee.db import Database

app = Flask(__name__)
Bootstrap(app)

if os.getenv('WAPP_SETTINGS'):
    app.config.from_envvar('WAPP_SETTINGS', silent=False)
else:
    app.config.from_pyfile('owntracks.cfg', silent=False)
    
db = Database(app)

# Here I would set up the cache, a task queue, etc.


if not app.debug:
    import logging
    from logging.handlers import SMTPHandler
    mail_handler = SMTPHandler('127.0.0.1',
                               'server-error@example.com',
                               app.config['ADMINS'],
                                 'YourApplication Failed')
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)
