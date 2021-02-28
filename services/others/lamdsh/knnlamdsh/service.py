from flask import request
from flask_restx import Resource, Namespace
from .core import get_knn_resourcesmetadata
from ....iomodels import input_def_knn_res, output_def

ns_lamdsh = Namespace('others',
                       description='Fetch/Compute doc2vec vector')

input_def = ns_lamdsh.model(*input_def_knn_res)
output_def = ns_lamdsh.model(*output_def)


@ns_lamdsh.route("/lamdsh/knnlamdsh", doc=False)
class KnnlamdshOthers(Resource):
    '''This is a test'''
    @ns_lamdsh.expect(input_def, validate=True)
    @ns_lamdsh.marshal_with(output_def)
    def post(self):
        '''Fetch/Compute knn doc2vec vector for a specific resource for lam-dashboard'''
        tmp = get_knn_resourcesmetadata(**request.json)
        # print(tmp)
        return {'output': tmp}

    @ns_lamdsh.errorhandler
    def default_error_handler(error):
        '''Default error handler'''
        return {'message': str(error)}, getattr(error, 'code', 500)
