from flask import request
from flask_restx import Resource, Namespace
from .core import get_resource_to_remove_from_sequence
from ...iomodels import input_def_sequence, output_def#_sequence_distance

ns_remove_from_sequence = Namespace('sequencing',
                                    description='Deal with ordered sequences')

input_def = ns_remove_from_sequence.model(*input_def_sequence)
output_def = ns_remove_from_sequence.model(*output_def)


@ns_remove_from_sequence.route("/removefromsequence")
class RemoveFromSequenceSequencing(Resource):
    @ns_remove_from_sequence.expect(input_def, validate=True)
    @ns_remove_from_sequence.marshal_with(output_def)
    def post(self):
        '''Return a resource id that should be removed from the sequence'''
        return {'output': get_resource_to_remove_from_sequence(**request.json)}

    @ns_remove_from_sequence.errorhandler
    def default_error_handler(error):
        '''Default error handler'''
        return {'message': str(error)}, getattr(error, 'code', 500)
