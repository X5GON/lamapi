from flask import request
from flask_restx import Resource, Namespace
from .core import doc2vec_model_update_DB
from ....iomodels import input_def_update, output_def

ns_doc2vec = Namespace('distance/doc2vec',
                       description='Fetch/Compute doc2vec vector')

input_def = ns_doc2vec.model(*input_def_update)
output_def = ns_doc2vec.model(*output_def)


@ns_doc2vec.route("/update", doc=False)
class UpdateDoc2vec(Resource):
    '''This is a test'''
    @ns_doc2vec.expect(input_def, validate=True)
    @ns_doc2vec.marshal_with(output_def)
    def post(self):
        '''Upadte doc2vec vectors in the DB'''
        return {'output': doc2vec_model_update_DB(request.json['model'], request.json['resume'], request.json['exp_id'])}

    @ns_doc2vec.errorhandler
    def default_error_handler(error):
        '''Default error handler'''
        return {'message': str(error)}, getattr(error, 'code', 500)
