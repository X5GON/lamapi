from flask import Flask, request, g
# from flask_restplus import Api
from werkzeug.utils import cached_property
from flask_restx import Api
from flask_cors import CORS
from flask_compress import Compress
from werkzeug.middleware.proxy_fix import ProxyFix
import time
import logging as log

from utils import get_args

def load_models():
     from x5gonwp3models.modelloader import load_models, AUTO_LOAD
     load_models(AUTO_LOAD)

from services.distance.config import namespaces as ns_distance
from services.hardness.config import namespaces as ns_hardness
from services.missingresource.config import namespaces as ns_missingresource
from services.ordonize.config import namespaces as ns_ordonize
from services.preprocess.config import namespaces as ns_preprocess
from services.temporal.config import namespaces as ns_temporal
from services.others.config import namespaces as ns_others
from services.recommendsystem.config import namespaces as ns_recommendsystem
from services.searchengine.config import namespaces as ns_searchengine
from services.sequencing.config import namespaces as ns_sequencing


namespaces = [*ns_temporal, *ns_distance, *ns_hardness, *ns_missingresource, *ns_ordonize, *ns_preprocess, *ns_others, *ns_recommendsystem, *ns_searchengine, *ns_sequencing]


class Server(object):
    def __init__(self):
        self.app = Flask(__name__)
        Compress(self.app)
        CORS(self.app)
        self.app.wsgi_app = ProxyFix(self.app.wsgi_app, x_proto=1, x_host=1)
        self.api = Api(self.app,
                       version='1.0',
                       title='X5-GON models API',
                       description='API providing endpoints to models developped by the WP3 of X5-GON project.'
                       )

    def initialize_app(self):
        for ns in namespaces:
            self.api.add_namespace(ns)

    def run(self, debug, port, host, cert, key):
        # self.app.run(port=port, host=host, debug=debug, ssl_context='adhoc')
        ssl_cxt = (cert, key)
        if cert =='' or key == '':
            ssl_cxt = 'adhoc'
        self.app.run(passthrough_errors=False, threaded=True, port=port, host=host, debug=debug, ssl_context=ssl_cxt)
        # self.app.run(port=port, host=host, debug=debug)


server = Server()


@server.app.before_request
def request_started():
    "Log HTTP request details"
    if (
        request.method == 'POST'
    ):
        g.start = time.time()
        ip_address = request.headers.get("X-Forwarded-For", request.remote_addr)
        host = request.host.split(":", 1)[0]
        params = dict(request.json)
        request_params = {
            "method": request.method,
            "path": request.path,
            "status": '',
            "size": request.content_length,
            "duration": '0',
            "ip": ip_address,
            "host": host,
            "params": params,
        }
        logger.info("request_begin", extra=request_params)


@server.app.after_request
def request_finished(response):
    "Log HTTP request details"
    if (
        request.method != 'POST'
    ):
        return response
    now = time.time()
    duration = round(now - g.start, 6)
    ip_address = request.headers.get("X-Forwarded-For", request.remote_addr)
    host = request.host.split(":", 1)[0]
    params = dict(request.json)
    log_params = {
        "method": request.method,
        "path": request.path,
        "status": response.status_code,
        "size": response.content_length,
        "duration": duration,
        "ip": ip_address,
        "host": host,
        "params": params,
    }
    logger.info("request_end", extra=log_params)
    return response


if __name__ == '__main__':
    args = get_args()
    handler = log.handlers.RotatingFileHandler('log/services_requests.log',
                                               mode='a',
                                               maxBytes=100*1024*1024,
                                               backupCount=1000)
    logger = log.getLogger('edrqlog')
    logger_formatter = log.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(method)s - %(path)s - %(status)s - %(size)s bytes - %(duration)s sec - %(ip)s - %(host)s - %(params)s')
    handler.setFormatter(logger_formatter)
    logger.setLevel(log.INFO)
    logger.addHandler(handler)
    load_models()
    server.initialize_app()
    server.run(debug=args.debug, host=args.host, port=args.port, cert=args.cert, key=args.key)
