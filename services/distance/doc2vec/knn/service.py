from flask import request
from flask_restx import Resource, Namespace
from .core import knn_doc2vec_res, knn_doc2vec_text, knn_doc2vec_vect
from ....iomodels import input_def_knn_res, input_def_knn_text, input_def_knn_vect_doc2vec, output_def

ns_doc2vec = Namespace('distance/doc2vec',
                       description='Fetch/Compute doc2vec vector')


input_def_text = ns_doc2vec.model(*input_def_knn_text)
input_def_res = ns_doc2vec.model(*input_def_knn_res)
input_def_vect = ns_doc2vec.model(*input_def_knn_vect_doc2vec)
output_def = ns_doc2vec.model(*output_def)


@ns_doc2vec.route("/knn/res")
class KnnDoc2vecres(Resource):
    '''This is a test'''
    @ns_doc2vec.expect(input_def_res, validate=True)
    @ns_doc2vec.marshal_with(output_def)
    def post(self):
        '''Fetch/Compute knn doc2vec vector for a specific resource'''
        return {'output': knn_doc2vec_res(**request.json)}

    @ns_doc2vec.errorhandler
    def default_error_handler(error):
        '''Default error handler'''
        return {'message': str(error)}, getattr(error, 'code', 500)


@ns_doc2vec.route("/knn/vector")
class KnnTDoc2vecVect(Resource):
    '''This is a test'''
    @ns_doc2vec.expect(input_def_vect, validate=True)
    @ns_doc2vec.marshal_with(output_def)
    def post(self):
        '''Compute knn Doc2vec vector for a given doc2vec vector (Vector specification/format must be respected: refer to fetch endpoint to know the suitable format)'''
        return {'output': knn_doc2vec_vect(**request.json)}

    @ns_doc2vec.errorhandler
    def default_error_handler(error):
        '''Default error handler'''
        return {'message': str(error)}, getattr(error, 'code', 500)


@ns_doc2vec.route("/knn/text")
class KnnDoc2vectext(Resource):
    '''This is a test'''
    @ns_doc2vec.expect(input_def_text, validate=True)
    @ns_doc2vec.marshal_with(output_def)
    def post(self):
        '''Fetch/Compute knn doc2vec vector for a specific resource'''
        return {'output': knn_doc2vec_text(**request.json)}

    @ns_doc2vec.errorhandler
    def default_error_handler(error):
        '''Default error handler'''
        return {'message': str(error)}, getattr(error, 'code', 500)
