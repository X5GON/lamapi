from flask import request
from flask_restx import Resource, Namespace
from .core import knn_tfidf_res, knn_tfidf_text, knn_tfidf_vect
from ....iomodels import input_def_knn_text, input_def_knn_res, input_def_knn_vect, output_def

ns_text2tfidf = Namespace('distance/text2tfidf',
                          description='Fetch/Compute tfidf vector')


input_def_text = ns_text2tfidf.model(*input_def_knn_text)
input_def_res = ns_text2tfidf.model(*input_def_knn_res)
input_def_vect = ns_text2tfidf.model(*input_def_knn_vect)
output_def = ns_text2tfidf.model(*output_def)


@ns_text2tfidf.route("/knn/res")
class KnnTfidfRes(Resource):
    '''This is a test'''
    @ns_text2tfidf.expect(input_def_res, validate=True)
    @ns_text2tfidf.marshal_with(output_def)
    def post(self):
        '''Fetch/Compute knn Tfidf vector for a specific resource'''
        return {'output': knn_tfidf_res(**request.json)}

    @ns_text2tfidf.errorhandler
    def default_error_handler(error):
        '''Default error handler'''
        return {'message': str(error)}, getattr(error, 'code', 500)


@ns_text2tfidf.route("/knn/vector")
class KnnTfidfVect(Resource):
    '''This is a test'''
    @ns_text2tfidf.expect(input_def_vect, validate=True)
    @ns_text2tfidf.marshal_with(output_def)
    def post(self):
        '''Compute knn Tfidf vector for a given tfidf vector (Vector specification/format must be respected: refer to fetch endpoint to know the suitable format)'''
        return {'output': knn_tfidf_vect(**request.json)}

    @ns_text2tfidf.errorhandler
    def default_error_handler(error):
        '''Default error handler'''
        return {'message': str(error)}, getattr(error, 'code', 500)


@ns_text2tfidf.route("/knn/text")
class KnnTfidfText(Resource):
    '''This is a test'''
    @ns_text2tfidf.expect(input_def_text, validate=True)
    @ns_text2tfidf.marshal_with(output_def)
    def post(self):
        '''Compute knn Tfidf vector for a given text'''
        return {'output': knn_tfidf_text(**request.json)}

    @ns_text2tfidf.errorhandler
    def default_error_handler(error):
        '''Default error handler'''
        return {'message': str(error)}, getattr(error, 'code', 500)
