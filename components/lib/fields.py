from flask_restx import fields


rid_field = fields.Integer(description='Resource id',
                           required=True,
                           example=39435)
rids_field = fields.List(rid_field,
                         description="List of resource ids",
                         min_items=1,
                         max_items=1000)

text_field = fields.String(description='Raw text',
                           required=True,
                           example='Lorem ipsum ...',
                           min_length=1,
                           max_length=1e8)
texts_field = fields.List(text_field,
                          description="List of raw text",
                          min_items=1,
                          max_items=10)

pos_field = fields.String(description='Part of speech class',
                          choices=['ADP',
                                   'ADV',
                                   'AUX',
                                   'CONJ',
                                   'CCCONJ',
                                   'DET',
                                   'INTJ',
                                   'NUM',
                                   'PART',
                                   'PRON',
                                   'PUNCT',
                                   'SCONJ',
                                   'SYM',
                                   'X'])
