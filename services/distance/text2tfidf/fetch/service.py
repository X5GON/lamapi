from flask import request
from flask_restx import Resource, Namespace
from .core import get_resource_tfidf
from ....iomodels import input_def_tfidf_fetch, output_def


ns_text2tfidf = Namespace('distance/text2tfidf',
                          description='Fetch/Compute tfidf vector')

input_def = ns_text2tfidf.model(*input_def_tfidf_fetch)
output_def = ns_text2tfidf.model(*output_def)


@ns_text2tfidf.route("/fetch")
class FetchText2tfidf(Resource):
    '''This is a test'''
    @ns_text2tfidf.expect(input_def, validate=True)
    @ns_text2tfidf.marshal_with(output_def)
    def post(self):
        '''Get computed tfidf vector from DB'''
        return {'output': get_resource_tfidf(**request.json)}

    @ns_text2tfidf.errorhandler
    def default_error_handler(error):
        '''Default error handler'''
        return {'message': str(error)}, getattr(error, 'code', 500)
