from flask_restx import fields, Model
from .fields import rids_field, pos_field, texts_field

# Input Models
# General input model (fetch from ids...)
input_def = ("input_def", {'resource_ids':  rids_field})

# Preprocess input def model(res):
input_preprocess = ("input_preprocess",
                    {'remove_pos': fields.List(pos_field,
                                               description="Part of speech to remove in the \
                                                            input text. Complete list can be \
                                                            found on SpacyNLP website: \
                                                            'https://spacy.io/api/annotation'",
                                               required=False),
                     'remove_stopwords': fields.Boolean(description='Boolean specifying \
                                                                     whether stop words \
                                                                     should be removed in \
                                                                     the processed text',
                                                        required=False,
                                                        example=True,
                                                        default=False),
                     'lemmatize': fields.Boolean(description='Boolean specifying \
                                                              whether the lemmatization \
                                                              should be applied on the \
                                                              processed text',
                                                 required=False,
                                                 example=True,
                                                 default=False),
                     'phrase': fields.String(description='Boolean specifying \
                                                            whether the phrased should \
                                                            be applied on the \
                                                            processed text. Several model are \
                                                            avalaible. Detailled explenation \
                                                            can be found at \
                                                            https://radimrehurek.com/gensim/models/phrases.html',
                                             required=False,
                                             choices=['x5gon',
                                                      'wikipedia',
                                                      None],
                                             example=False,
                                             default=None),
                     'lowercase': fields.Boolean(description='Boolean specifying \
                                                              whether the processed text \
                                                              should be lowercesad.',
                                                 required=False,
                                                 example=True,
                                                 default=False),
                     'dfxp2text': fields.Boolean(description='Give the text version of the \
                                                              dfxp input text',
                                                 title="Dfxp to text",
                                                 required=False,
                                                 example=False,
                                                 default=False)
                     })

input_preprocess_fetch = Model.inherit('input_preprocess_fetch',
                                       input_preprocess,
                                       {"resource_ids": rids_field})

input_preprocess_text = Model.inherit('input_preprocess_text',
                                      input_preprocess,
                                      {"texts": texts_field})
