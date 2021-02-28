from flask import request
from flask_restx import Resource, Namespace
from .core import continuous_doc2vec_model_update_DB
from ....iomodels import input_def_update, output_def


ns_continuousdoc2vec = Namespace('temporal/continuousdoc2vec',
                                 description='Fetch/Compute continuousdoc2vec vector')

input_def = ns_continuousdoc2vec.model(*input_def_update)
output_def = ns_continuousdoc2vec.model(*output_def)


@ns_continuousdoc2vec.route("/update", endpoint='update', doc=False)
class UpdateContinuousDoc2vec(Resource):
    '''This is a test'''
    @ns_continuousdoc2vec.expect(input_def, validate=True)
    @ns_continuousdoc2vec.marshal_with(output_def)
    def post(self):
        '''Update computed continuousdoc2vec vectors in the DB'''
        return {'output': continuous_doc2vec_model_update_DB(**request.json)}

    @ns_continuousdoc2vec.errorhandler
    def default_error_handler(error):
        '''Default error handler'''
        return {'message': str(error)}, getattr(error, 'code', 500)
