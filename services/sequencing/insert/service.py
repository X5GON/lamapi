from flask import request
from flask_restx import Resource, Namespace
from .core import get_resources_to_insert
from ...iomodels import input_def_insert_in_sequence, output_def#_sequence_distance

ns_insert = Namespace('sequencing',
                      description='Deal with ordered sequences')

input_def = ns_insert.model(*input_def_insert_in_sequence)
output_def = ns_insert.model(*output_def)#_sequence_distance)


@ns_insert.route("/insert")
class InsertSequencing(Resource):
    @ns_insert.expect(input_def, validate=True)
    @ns_insert.marshal_with(output_def)
    def post(self):
        '''Suggest resources to insert between two resources in a sequence'''
        return {'output': get_resources_to_insert(**request.json)}

    @ns_insert.errorhandler
    def default_error_handler(error):
        '''Default error handler'''
        return {'message': str(error)}, getattr(error, 'code', 500)
