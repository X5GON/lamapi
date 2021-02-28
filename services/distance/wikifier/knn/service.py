from flask import request
from flask_restx import Resource, Namespace
from .core import knn_wikifier_res, knn_wikifier_text, knn_wikifier_vect
from ....iomodels import input_def_knn_text, input_def_knn_res, input_def_knn_vect, output_def

ns_wikifier = Namespace('distance/wikifier',
                        description='Fetch/Compute wikifier vector')


input_def_text = ns_wikifier.model(*input_def_knn_text)
input_def_res = ns_wikifier.model(*input_def_knn_res)
input_def_vect = ns_wikifier.model(*input_def_knn_vect)
output_def = ns_wikifier.model(*output_def)


@ns_wikifier.route("/knn/res")
class KnnWikifierRes(Resource):
    '''This is a test'''
    @ns_wikifier.expect(input_def_res, validate=True)
    @ns_wikifier.marshal_with(output_def)
    def post(self):
        '''Fetch/Compute knn wikifier vector for a specific resource'''
        return {'output': knn_wikifier_res(**request.json)}

    @ns_wikifier.errorhandler
    def default_error_handler(error):
        '''Default error handler'''
        return {'message': str(error)}, getattr(error, 'code', 500)


@ns_wikifier.route("/knn/vector")
class KnnWikifierVect(Resource):
    '''This is a test'''
    @ns_wikifier.expect(input_def_vect, validate=True)
    @ns_wikifier.marshal_with(output_def)
    def post(self):
        '''Compute knn Wikifier vector for a given wikifier vector (Vector specification/format must be respected: refer to fetch endpoint to know the suitable format)'''
        return {'output': knn_wikifier_vect(**request.json)}

    @ns_wikifier.errorhandler
    def default_error_handler(error):
        '''Default error handler'''
        return {'message': str(error)}, getattr(error, 'code', 500)


@ns_wikifier.route("/knn/text")
class KnnWikifierText(Resource):
    '''This is a test'''
    @ns_wikifier.expect(input_def_text, validate=True)
    @ns_wikifier.marshal_with(output_def)
    def post(self):
        '''Compute knn wikifier vector for a given text'''
        return {'output': knn_wikifier_text(**request.json)}

    @ns_wikifier.errorhandler
    def default_error_handler(error):
        '''Default error handler'''
        return {'message': str(error)}, getattr(error, 'code', 500)
