from flask import request
from flask_restx import Resource, Namespace
from .core import get_resource_continuousdoc2vec
from ....iomodels import input_def, output_def


ns_continuousdoc2vec = Namespace('temporal/continuousdoc2vec',
                                 description='Fetch/Compute continuousdoc2vec vector')

input_def = ns_continuousdoc2vec.model(*input_def)
output_def = ns_continuousdoc2vec.model(*output_def)


@ns_continuousdoc2vec.route("/fetch")
class FetchContinuousDoc2vec(Resource):
    '''This is a test'''
    @ns_continuousdoc2vec.expect(input_def, validate=True)
    @ns_continuousdoc2vec.marshal_with(output_def)
    def post(self):
        '''Get computed continuousdoc2vec vector from DB. The idea is to no longer representing the resource as a big indivisible block. But on the contrary as an object whose content and therefore the concepts related to it evolve as the resource is consumed.This approach reduces the bias due to the comparison of resources of very different sizes. And also allows in particular for long resources to better capture the meaning of the content. For example, a 200-page book on computer science does not look at all like the same resources in its first chapter, where it deals with the history of computer science, and in its last chapter, where it deals with the challenges of tomorrow's computer science. Practically, we simply cut the whole transitions of the resource in constant sized chunk of 5000 words without overlapping between chunks. For each chunk, we simply compute the corresponding (wikifier, doc2vec) and wrap all these results in an output list.'''
        return {'output': get_resource_continuousdoc2vec(**request.json)}

    @ns_continuousdoc2vec.errorhandler
    def default_error_handler(error):
        '''Default error handler'''
        return {'message': str(error)}, getattr(error, 'code', 500)
