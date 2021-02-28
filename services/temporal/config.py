from flask_restx import Namespace
from .continuousdoc2vec.config import namespaces as ns_continuousdoc2vec
from .continuouswikifier.config import namespaces as ns_continuouswikifier

ns_temporal = Namespace('temporal',
                        description='temporal tools')

namespaces = [ns_temporal, *ns_continuousdoc2vec, *ns_continuouswikifier]
