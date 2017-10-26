import logging
import os

from flask import Flask, Response, url_for
from werkzeug.wsgi import DispatcherMiddleware

from forum.application import Application
from forum.cache import cache

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config['APPLICATION_ROOT'] = '/api'
app.config['CACHE_TYPE'] = os.environ['CACHE_TYPE']
app.config['CACHE_THRESHOLD'] = 10 ** 6
cache.init_app(app)

application = Application()
application.register(app)


def simple(env, resp):
    resp('404 NOT FOUND', [('mimetype', 'application/json')])
    return [b'']


app.wsgi_app = DispatcherMiddleware(simple, {'/api': app.wsgi_app})
logging.info("[app.py] add DispatcherMiddleware")


if __name__ == '__main__':
    logging.info("try start")
    app.run()
