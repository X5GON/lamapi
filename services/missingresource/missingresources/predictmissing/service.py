from flask import request
from flask_restx import Resource, Namespace
from .core import predict_missing_deponcandidatetype
from ....iomodels import input_def_missingresource, output_def

ns_missingresources = Namespace('missingresource/missingresources',
                                description='Compute/Predict the missing resource')

input_def = ns_missingresources.model(*input_def_missingresource)
output_def = ns_missingresources.model(*output_def)


@ns_missingresources.route("/predictmissing")
class PredictmissingMissingresources(Resource):
    '''This is a test'''
    @ns_missingresources.expect(input_def, validate=True)
    @ns_missingresources.marshal_with(output_def)
    def post(self):
        '''Predict the missing resource'''
        return {'output': predict_missing_deponcandidatetype(previous=request.json['previous'], after=request.json['after'], candidate_ids=request.json['candidate_ids'])}

    @ns_missingresources.errorhandler
    def default_error_handler(error):
        '''Default error handler'''
        return {'message': str(error)}, getattr(error, 'code', 500)
