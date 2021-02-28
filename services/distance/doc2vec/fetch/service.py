from .core import get_resource_doc2vec
from ....iomodels import output_def
from components.lib.input_models import input_def
from components.lib.services import ServicesFactory
from flask_restx import Namespace


ns_doc2vec = Namespace('distance/doc2vec',
                       description='Fetch/Compute doc2vec vector')

ServicesFactory.create_service(input_model=input_def,
                               output_model=output_def,
                               route="/fetch",
                               ns=ns_doc2vec,
                               on_call=get_resource_doc2vec)
