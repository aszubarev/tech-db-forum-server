import logging
import os

from flask import Flask, Response, url_for
from werkzeug.wsgi import DispatcherMiddleware

from tech_forum_api.application import Application

logging.basicConfig(level=logging.INFO)
logging.exception("HERE HELLO APP.PY")


app = Flask(__name__)
app.config['APPLICATION_ROOT'] = '/api'

application = Application()
application.register(app)

logging.info("[APP.PY] registered blueprints")


@app.errorhandler(400)
def bad_request(error):
    logging.info(error)
    return Response(status=400, mimetype='application/json')


@app.errorhandler(404)
def data_not_found(error):
    logging.info(error)
    return Response(status=404, mimetype='application/json')


@app.errorhandler(409)
def restrict_violation(error):
    logging.info(error)
    return Response(status=409, mimetype='application/json')


@app.errorhandler(500)
def internal_server_error(error):
    logging.exception(error)
    return Response(status=500, mimetype='application/json')


def simple(env, resp):
    logging.debug(env)
    resp('404 NOT FOUND', [('mimetype', 'application/json')])
    return [b'']


# app.wsgi_app = DispatcherMiddleware(simple, {'/': app.wsgi_app})
# logging.info("[APP.PY] add DispatcherMiddleware")


if __name__ == '__main__':
    logging.info("try start")
    app.run()
