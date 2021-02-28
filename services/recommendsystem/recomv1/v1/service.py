from flask import request
from flask_restx import Resource, Namespace
from .core import get_resource_recommend_v1
from ....iomodels import input_def_recommend_v1, output_def

ns_recomv1 = Namespace('recommendsystem',
                       description='First version of the recommendation system based on KNN models')

input_def = ns_recomv1.model(*input_def_recommend_v1)
output_def = ns_recomv1.model(*output_def)


@ns_recomv1.route("/v1")
class GetRecommendv1(Resource):
    '''This is a test'''
    @ns_recomv1.expect(input_def, validate=True)
    @ns_recomv1.marshal_with(output_def)
    def post(self):
        '''Compute the recommendation list based on Knn models'''
        return {'output': get_resource_recommend_v1(**request.json)}

    @ns_recomv1.errorhandler
    def default_error_handler(error):
        '''Default error handler'''
        return {'message': str(error)}, getattr(error, 'code', 500)
