from flask import request
from flask_restx import Resource, Namespace
from .core import get_mdlplgnoeracs_data
from ....iomodels import input_def_mdlx5gnoeracs, output_def_mdlx5gnoeracs

ns_moodle = Namespace('others',
                      description='Fetch/Compute needed data for x5gon mdl plugin')

input_def = ns_moodle.model(*input_def_mdlx5gnoeracs)
output_def = ns_moodle.model(*output_def_mdlx5gnoeracs)


@ns_moodle.route("/moodle/x5plgn/oeracs")
class X5plgnoeracsMoodle(Resource):
    '''This is a test'''
    @ns_moodle.expect(input_def, validate=True)
    # @ns_moodle.marshal_with(output_def)
    def post(self):
        '''Get oer access data within group/course inside x5gon moodle plugin'''
        return get_mdlplgnoeracs_data(request.json)

    @ns_moodle.errorhandler
    def default_error_handler(error):
        '''Default error handler'''
        return {'message': str(error)}, getattr(error, 'code', 500)
