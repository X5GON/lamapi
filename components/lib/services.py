from flask_restx import Resource
from flask import request


class ServicesFactory:
    def __init__(self):
        pass

    @staticmethod
    def create_service(input_model,
                       output_model,
                       route,
                       ns,
                       on_call):

        input_def = ns.model(*input_model)
        output_def = ns.model(*output_model)

        @ns.route(route)
        class MyService(Resource):
            @ns.expect(input_def, validate=True)
            @ns.marshal_with(output_def)
            def post(self):
                return {'output': on_call(**request.json)}

            @ns.errorhandler
            def default_error_handler(error):
                return {'message': str(error)}, getattr(error, 'code', 500)
        return MyService
