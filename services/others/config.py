from flask_restx import Namespace
from .lamdsh.config import namespaces as ns_lamdsh
from .modelsdsh.config import namespaces as ns_modelsdash
from .moodle.config import namespaces as ns_moodle

ns_others = Namespace('others',
                      description='others oers meta infos tools')

namespaces = [ns_others, *ns_lamdsh, *ns_modelsdash, *ns_moodle]
