from flask import request
from flask_restx import Resource, Namespace
from .core import get_resource_search_v1
from ....iomodels import input_def_searchv1, output_def

ns_searchv1 = Namespace('searchengine',
                        description='First version of search engine')

input_def = ns_searchv1.model(*input_def_searchv1)
output_def = ns_searchv1.model(*output_def)


@ns_searchv1.route("/v1")
class Getsearchv1(Resource):
    '''This is a test'''
    @ns_searchv1.expect(input_def, validate=True)
    @ns_searchv1.marshal_with(output_def)
    def post(self):
        '''Get search results based on Knn models'''
        return {'output': get_resource_search_v1(**request.json)}

    @ns_searchv1.errorhandler
    def default_error_handler(error):
        '''Default error handler'''
        return {'message': str(error)}, getattr(error, 'code', 500)
