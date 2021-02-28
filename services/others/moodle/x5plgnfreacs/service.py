from flask import request
from flask_restx import Resource, Namespace
from .core import store_mdl_group_data
from ....iomodels import input_def_mdlx5gnfreacs, output_def_mdlx5gnfreacs

ns_moodle = Namespace('others',
                      description='Fetch/Compute needed data for x5gon mdl plugin')

input_def = ns_moodle.model(*input_def_mdlx5gnfreacs)
output_def = ns_moodle.model(*output_def_mdlx5gnfreacs)


@ns_moodle.route("/moodle/x5plgn/freacs")
class X5plgnfreacsMoodle(Resource):
    '''This is a test'''
    @ns_moodle.expect(input_def, validate=True)
    # @ns_moodle.marshal_with(output_def)
    def post(self):
        '''Store group/course data on x5gon feature access inside x5gon moodle plugin'''
        return {"output": store_mdl_group_data(request.json)}

    @ns_moodle.errorhandler
    def default_error_handler(error):
        '''Default error handler'''
        return {'message': str(error)}, getattr(error, 'code', 500)
