from flask_restx import Namespace
from .missingresources.config import namespaces as ns_missingresources

ns_missingresource = Namespace('missingresource',
                                description='missingresource tools')

namespaces = [ns_missingresource, *ns_missingresources]
