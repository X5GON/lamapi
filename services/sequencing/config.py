from flask_restx import Namespace
from .sort.service import ns_sort
from .insert.service import ns_insert
from .removefromsequence.service import ns_remove_from_sequence
from .removefrombasket.service import ns_remove_from_basket

ns_sequencing = Namespace('sequencing',
                          description='Management of ordered sequences')

namespaces = [ns_sequencing, ns_sort, ns_insert, ns_remove_from_sequence, ns_remove_from_basket]
