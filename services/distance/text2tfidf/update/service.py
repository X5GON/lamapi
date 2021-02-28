from flask import request
from flask_restx import Resource, Namespace
from .core import tfidf_model_update_DB
from ....iomodels import input_def_update, output_def

ns_text2tfidf = Namespace('distance/text2tfidf',
                          description='Fetch/Compute tfidf vector')

input_def = ns_text2tfidf.model(*input_def_update)
output_def = ns_text2tfidf.model(*output_def)


@ns_text2tfidf.route("/update", doc=False)
class UpdateText2tfidf(Resource):
    '''This is a test'''
    @ns_text2tfidf.expect(input_def, validate=True)
    @ns_text2tfidf.marshal_with(output_def)
    def post(self):
        '''Update tfidf vectors in the DB'''
        return {'output': tfidf_model_update_DB(request.json['resume'], request.json['exp_id'])}

    @ns_text2tfidf.errorhandler
    def default_error_handler(error):
        '''Default error handler'''
        return {'message': str(error)}, getattr(error, 'code', 500)
