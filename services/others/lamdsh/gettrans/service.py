from flask import request
from flask_restx import Resource, Namespace
from .core import get_resource_lamdshtrans
from ....iomodels import input_def_lamdshtrans, output_def

ns_lamdsh = Namespace('others',
                      description='Fetch/Compute other useful infos for lam-dashboard')

input_def = ns_lamdsh.model(*input_def_lamdshtrans)
output_def = ns_lamdsh.model(*output_def)


@ns_lamdsh.route("/lamdsh/gettrans", doc=False)
class GettransLamdsh(Resource):
    '''This is a test'''
    @ns_lamdsh.expect(input_def, validate=True)
    @ns_lamdsh.marshal_with(output_def)
    def post(self):
        '''Get transcriptions(Original + EngTrans) from DB for lam-dashboard'''
        return {'output': get_resource_lamdshtrans(request.json)}

    @ns_lamdsh.errorhandler
    def default_error_handler(error):
        '''Default error handler'''
        return {'message': str(error)}, getattr(error, 'code', 500)
