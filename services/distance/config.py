from flask_restx import Namespace
from .doc2vec.config import namespaces as ns_doc2vec
from .text2tfidf.config import namespaces as ns_text2tfidf
from .wikifier.config import namespaces as ns_wikifier

ns_distance = Namespace('distance',
                        description='distance tools')

namespaces = [ns_distance, *ns_doc2vec, *ns_text2tfidf, *ns_wikifier]
