from flask import request
from flask_restx import Resource, Namespace
from .core import get_resource_wikifier, get_wikifier
from ....iomodels import input_def_wikification_text, input_def_wikification_fetch, output_def


ns_wikifier = Namespace('distance/wikifier',
                        description='Fetch/Compute wikifier vector')

input_def_text = ns_wikifier.model(*input_def_wikification_text)
input_def_fetch = ns_wikifier.model(*input_def_wikification_fetch)
output_def = ns_wikifier.model(*output_def)


@ns_wikifier.route("/fetch")
class FetchWikifierRes(Resource):
    '''This is a test'''
    @ns_wikifier.expect(input_def_fetch, validate=True)
    @ns_wikifier.marshal_with(output_def)
    def post(self):
        '''Get computed wikifier vector from DB'''
        return {'output': get_resource_wikifier(**request.json)}

    @ns_wikifier.errorhandler
    def default_error_handler(error):
        '''Default error handler'''
        return {'message': str(error)}, getattr(error, 'code', 500)


@ns_wikifier.route("/text")
class FetchWikifierText(Resource):
    '''This is a test'''
    @ns_wikifier.expect(input_def_text, validate=True)
    @ns_wikifier.marshal_with(output_def)
    def post(self):
        '''Get computed wikifier vector from DB'''
        return {'output': get_wikifier(**request.json)}

    @ns_wikifier.errorhandler
    def default_error_handler(error):
        '''Default error handler'''
        return {'message': str(error)}, getattr(error, 'code', 500)
