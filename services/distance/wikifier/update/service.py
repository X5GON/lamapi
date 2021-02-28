from flask import request
from flask_restx import Resource, Namespace
from .core import wikifier_model_update_DB
from ....iomodels import input_def_update, output_def

ns_wikifier = Namespace('distance/wikifier',
                        description='Fetch/Compute wikifier vector')
input_def = ns_wikifier.model(*input_def_update)
output_def = ns_wikifier.model(*output_def)


@ns_wikifier.route("/update", doc=False)
class UpdateWikifier(Resource):
    '''This is a test'''
    @ns_wikifier.expect(input_def, validate=True)
    @ns_wikifier.marshal_with(output_def)
    def post(self):
        '''Update wikifier vectors in the DB'''
        return {'output': wikifier_model_update_DB(request.json['resume'], request.json['exp_id'])}

    @ns_wikifier.errorhandler
    def default_error_handler(error):
        '''Default error handler'''
        return {'message': str(error)}, getattr(error, 'code', 500)
