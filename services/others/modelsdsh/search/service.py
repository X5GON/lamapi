from flask import request
from flask_restx import Resource, Namespace
from .core import get_resource_modelsdshsearch
from ....iomodels import input_def_modelsdshsearch, output_def_modelsdshsearch

ns_modelsdsh = Namespace('others',
                         description='Fetch/Compute other useful infos for models-dashboard')

input_def = ns_modelsdsh.model(*input_def_modelsdshsearch)
output_def = ns_modelsdsh.model(*output_def_modelsdshsearch)


@ns_modelsdsh.route("/modelsdsh/search")
class Searchmodelsdsh(Resource):
    '''This is a test'''
    @ns_modelsdsh.expect(input_def, validate=True)
    @ns_modelsdsh.marshal_with(output_def)
    def post(self):
        '''Get search results for modelsdsh'''
        return get_resource_modelsdshsearch(request.json)

    @ns_modelsdsh.errorhandler
    def default_error_handler(error):
        '''Default error handler'''
        return {'message': str(error)}, getattr(error, 'code', 500)
