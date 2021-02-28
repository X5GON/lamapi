from flask import request
from flask_restx import Resource, Namespace
from .core import preprocess_res, preprocess_text
from ..iomodels import input_def_preprocess_fetch, input_def_preprocess_text, output_def

ns_preprocess = Namespace('preprocess',
                          description='Preprocess a text depending on needed configs')

input_def_fetch = ns_preprocess.model(*input_def_preprocess_fetch)
input_def_text = ns_preprocess.model(*input_def_preprocess_text)
output_def = ns_preprocess.model(*output_def)


@ns_preprocess.route("/res")
class PreprocessRes(Resource):
    '''This is a test'''
    @ns_preprocess.expect(input_def_fetch, validate=True)
    @ns_preprocess.marshal_with(output_def)
    def post(self):
        '''Preprocessing given resources from the project DB in real time'''
        return {'output': preprocess_res(**request.json)}

    @ns_preprocess.errorhandler
    def default_error_handler(error):
        '''Default error handler'''
        return {'message': str(error)}, getattr(error, 'code', 500)


@ns_preprocess.route("/text")
class PreprocessText(Resource):
    '''This is a test'''
    @ns_preprocess.expect(input_def_text, validate=True)
    @ns_preprocess.marshal_with(output_def)
    def post(self):
        '''Preprocessing given texts in real time'''
        return {'output': preprocess_text(**request.json)}

    @ns_preprocess.errorhandler
    def default_error_handler(error):
        '''Default error handler'''
        return {'message': str(error)}, getattr(error, 'code', 500)
