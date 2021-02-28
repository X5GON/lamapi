from flask import request
from flask_restx import Resource, Namespace
from .core import get_resource_continuouswikifier
from ....iomodels import input_def_wikification_fetch, output_def


ns_continuouswikifier = Namespace('temporal/continuouswikifier',
                                  description='Fetch/Compute continuouswikifier vector')

input_def = ns_continuouswikifier.model(*input_def_wikification_fetch)
output_def = ns_continuouswikifier.model(*output_def)


@ns_continuouswikifier.route("/fetch")
class FetchContinuousWikifier(Resource):
    '''This is a test'''
    @ns_continuouswikifier.expect(input_def, validate=True)
    @ns_continuouswikifier.marshal_with(output_def)
    def post(self):
        '''Get computed continuouswikifier vector from DB'''
        return {'output': get_resource_continuouswikifier(**request.json)}

    @ns_continuouswikifier.errorhandler
    def default_error_handler(error):
        '''Default error handler'''
        return {'message': str(error)}, getattr(error, 'code', 500)
