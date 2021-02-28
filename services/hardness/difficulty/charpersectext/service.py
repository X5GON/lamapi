from flask import request
from flask_restx import Resource, Namespace
from .core import get_resource_difficulty
from ....iomodels import input_def_texts, output_def

ns_difficulty = Namespace('difficulty',
                          description='Compute difficulty scores')


input_def = ns_difficulty.model(*input_def_texts)
output_def = ns_difficulty.model(*output_def)


@ns_difficulty.route("/charpersec/text", doc=False)
class CharpersectextDifficulty(Resource):
    '''This is a test'''
    @ns_difficulty.expect(input_def, validate=True)
    @ns_difficulty.marshal_with(output_def)
    def post(self):
        '''Compute 'CharPerSec' difficulty scores for a given texts'''
        return {'output': get_resource_difficulty(request.json['resource_texts'])}

    @ns_difficulty.errorhandler
    def default_error_handler(error):
        '''Default error handler'''
        return {'message': str(error)}, getattr(error, 'code', 500)
