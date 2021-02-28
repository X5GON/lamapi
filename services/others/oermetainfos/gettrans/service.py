from flask import request
from flask_restx import Resource, Namespace
from .core import get_resource_oermetainfos
from ....iomodels import input_def, output_def

ns_oermetainfos = Namespace('others',
                      description='Fetch other infos')

input_def = ns_oermetainfos.model(*input_def)
output_def = ns_oermetainfos.model(*output_def)


@ns_oermetainfos.route("/oermetainfos/transcription")
class GettransOermetainfos(Resource):
    '''This is a test'''
    @ns_oermetainfos.expect(input_def, validate=True)
    @ns_oermetainfos.marshal_with(output_def)
    def post(self):
        '''Get computed other vector'''
        return {'output': get_resource_oermetainfos(request.json['resource_ids'])}

    @ns_oermetainfos.errorhandler
    def default_error_handler(error):
        '''Default error handler'''
        return {'message': str(error)}, getattr(error, 'code', 500)
