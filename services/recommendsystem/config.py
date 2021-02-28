from flask_restx import Namespace
from .recomv1.config import namespaces as ns_recomv1

ns_recommendsystem = Namespace('recommendsystem',
                               description='Recommendation system services')

namespaces = [ns_recommendsystem, *ns_recomv1]
