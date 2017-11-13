# from gevent import monkey
# monkey.patch_all()
# from gevent.pywsgi import WSGIServer

import logging

from flask import Flask
from werkzeug.wsgi import DispatcherMiddleware

from forum.application import Application


logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
application = Application()
application.register(app)


def simple(env, resp):
    resp('404 NOT FOUND', [('mimetype', 'application/json')])
    return [b'']


app.wsgi_app = DispatcherMiddleware(simple, {'/api': app.wsgi_app})

# http_server = WSGIServer(('', 5000), app.wsgi_app)


if __name__ == '__main__':
    app.run()
    # http_server.serve_forever()

