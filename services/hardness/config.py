from flask_restx import Namespace
from .difficulty.config import namespaces as ns_difficulty

ns_hardness = Namespace('hardness',
                        description='hardness tools')

namespaces = [ns_hardness, *ns_difficulty]
