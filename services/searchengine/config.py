from flask_restx import Namespace
from .searchv1.config import namespaces as ns_searchv1

ns_searchengine = Namespace('searchengine',
                            description='Search engine services')

namespaces = [ns_searchengine, *ns_searchv1]
