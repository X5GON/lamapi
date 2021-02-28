from flask import request
from flask_restx import Resource, Namespace
from .core import get_resource_to_remove_from_basket
from ...iomodels import input_def_basket, output_def

ns_remove_from_basket = Namespace('sequencing',
                                  description='Deal with ordered sequences')

input_def = ns_remove_from_basket.model(*input_def_basket)
output_def = ns_remove_from_basket.model(*output_def)


@ns_remove_from_basket.route("/removefrombasket")
class RemoveFromBasketSequencing(Resource):
    @ns_remove_from_basket.expect(input_def, validate=True)
    @ns_remove_from_basket.marshal_with(output_def)
    def post(self):
        '''Return a resource id that should be removed from the basket'''
        return {'output': get_resource_to_remove_from_basket(**request.json)}

    @ns_remove_from_basket.errorhandler
    def default_error_handler(error):
        '''Default error handler'''
        return {'message': str(error)}, getattr(error, 'code', 500)
