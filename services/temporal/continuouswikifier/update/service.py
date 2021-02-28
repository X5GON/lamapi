from flask import request
from flask_restx import Resource, Namespace
from .core import continuouswikifier_model_update_DB
from ....iomodels import input_def_update, output_def

ns_continuouswikifier = Namespace('temporal/continuouswikifier',
                                  description='Fetch/Compute continuouswikifier vector')
input_def = ns_continuouswikifier.model(*input_def_update)
output_def = ns_continuouswikifier.model(*output_def)


@ns_continuouswikifier.route("/update", doc=False)
class UpdateContinuousWikifier(Resource):
    '''This is a test'''
    @ns_continuouswikifier.expect(input_def, validate=True)
    @ns_continuouswikifier.marshal_with(output_def)
    def post(self):
        '''Update computed continuousdoc2vec vectors in the DB'''
        return {'output': continuouswikifier_model_update_DB(**request.json)}

    @ns_continuouswikifier.errorhandler
    def default_error_handler(error):
        '''Default error handler'''
        return {'message': str(error)}, getattr(error, 'code', 500)
