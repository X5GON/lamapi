from flask import request
from flask_restx import Resource, Namespace
from .core import get_sequence_and_distances
from ...iomodels import input_def_basket, output_def#_sequence_distance

ns_sort = Namespace('sequencing',
                    description='Deal with ordered sequences')

input_def = ns_sort.model(*input_def_basket)
output_def = ns_sort.model(*output_def)#_sequence_distance)


@ns_sort.route("/sort")
class SortBasketSequencing(Resource):
    @ns_sort.expect(input_def, validate=True)
    @ns_sort.marshal_with(output_def)
    def post(self):
        '''Compute a sequence from the given basket, and also return the distances between each pair in the sequence'''
        return {'output': get_sequence_and_distances(**request.json)}

    @ns_sort.errorhandler
    def default_error_handler(error):
        '''Default error handler'''
        return {'message': str(error)}, getattr(error, 'code', 500)
