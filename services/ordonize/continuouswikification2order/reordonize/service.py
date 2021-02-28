from flask import request
from flask_restx import Resource, Namespace
from .core import get_resource_continuouswikification2order
from ....iomodels import input_def_reordonize, output_def

ns_continuouswikification2order = Namespace('ordonize/continuouswikification2order',
                                            description='Compute the order depending on the continuouswikifier vectors')

input_def = ns_continuouswikification2order.model(*input_def_reordonize)
output_def = ns_continuouswikification2order.model(*output_def)


@ns_continuouswikification2order.route("/reordonize")
class ReordonizeContinuouswikification2order(Resource):
    '''This is a test'''
    @ns_continuouswikification2order.expect(input_def, validate=True)
    @ns_continuouswikification2order.marshal_with(output_def)
    def post(self):
        '''Reordonize resources depending on continuouswikifier vectors'''
        return {'output': get_resource_continuouswikification2order(**request.json)}

    @ns_continuouswikification2order.errorhandler
    def default_error_handler(error):
        '''Default error handler'''
        return {'message': str(error)}, getattr(error, 'code', 500)
