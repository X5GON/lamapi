from flask_restx import Namespace
from .continuouswikification2order.config import namespaces as ns_continuouswikification2order

ns_temporal = Namespace('ordonize',
                        description='ordonize tools')

namespaces = [ns_temporal, *ns_continuouswikification2order]
