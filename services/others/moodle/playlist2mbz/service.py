from flask import request, send_from_directory, after_this_request
from flask_restx import Resource, Namespace
from .core import build_mbz, clean_mbz
from ....iomodels import input_def_mdlplaylist2mbz, output_def_moodleplaylist2mbz
import json

ns_moodle = Namespace('others',
                      description='Fetch/Compute other useful infos for lam-dashboard')

input_def = ns_moodle.model(*input_def_mdlplaylist2mbz)
output_def = ns_moodle.model(*output_def_moodleplaylist2mbz)


@ns_moodle.route("/moodle/playlist2mbz")
class SearchMoodle(Resource):
    '''This is a test'''
    @ns_moodle.expect(input_def, validate=True)
    # @ns_moodle.marshal_with(output_def)
    def post(self):
        '''Build an mbz moodle course backup file from a playlist'''
        build_response = build_mbz(request.json)
        @after_this_request
        def remove_file(response):
            try:
                clean_mbz(build_response['mbz_folder'])
            except Exception as error:
                print("Error cleaning the mbz temporary files: ", error)
            return response
        try:
            if "playlist_format" in request.json and request.json['playlist_format'] == "json":
                return build_response['plst_obj']
            return send_from_directory(directory=build_response['directory'],
                                       filename=build_response['filename'],
                                       as_attachment=True)
        except Exception as error:
            print(error)
            return build_response

    @ns_moodle.errorhandler
    def default_error_handler(error):
        '''Default error handler'''
        return {'message': str(error)}, getattr(error, 'code', 500)
