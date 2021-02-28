from flask_restx import fields


# Input Models
# General input model (fetch from ids...)
input_def = ("input_def", {
    'resource_ids':  fields.List(fields.Integer(description='Instance id'),
                                 title="List of resources ids",
                                 description="An Integer list of resource ids in the project Database",
                                 required=True,
                                 example=[39435, 39426, 39425, 38657],
                                 min_items=1,
                                 max_items=1000)
})

# Preprocess input def model(res):
input_def_preprocess_fetch = ("input_def_preprocess_fetch", {
    'resource_ids':  fields.List(fields.Integer(description='Instance id'),
                                 title="List of resources ids",
                                 description="An Integer list of resource ids in the project Database",
                                 required=True,
                                 example=[39435, 39426, 39425, 38657],
                                 min_items=1,
                                 max_items=1000),
     'remove_pos':  fields.List(fields.String(description='Needed POS'),
                                title="Remove POS from text using SpacyNLP library",
                                description="Remove Part Of Speech: list of possible tags can be found in SpacyNLP library website: 'https://spacy.io/api/annotation'",
                                required=False,
                                example=['ADP',
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
                                         'X']),
     'remove_stopwords':  fields.Boolean(description='Remove stopwords from the given text',
                                         title="Remove Stop Words",
                                         required=False,
                                         example=True,
                                         default=False),
     'lemmatize':  fields.Boolean(description='Give the lemmatized version of the text',
                                  title="Lemmatize text",
                                  required=False,
                                  example=True,
                                  default=False),
     'phrase':  fields.String(description='Give the phrased version of the text',
                               title="Phrase text",
                               required=False,
                               choices=['x5gon','wikipedia', None],
                               example=False,
                               default=None),
     'lowercase':  fields.Boolean(description='Give the lowercase version of the text',
                                  title="Lowercase text",
                                  required=False,
                                  example=True,
                                  default=False),
     'dfxp2text':  fields.Boolean(description='Give the text version of the dfxp input text',
                                  title="Dfxp to text",
                                  required=False,
                                  example=False,
                                  default=False)
    })

# Preprocess input def model(text):
input_def_preprocess_text = ("input_def_preprocess_text", {
    'texts':  fields.List(fields.String(description='The given text'),
                          title="List of texts",
                          description="A list of texts needed to be preprocessed",
                          required=True,
                          example=['Go play away. Here is the NASA lab :p !', 'Go play away. Here is the NASA lab :p !'],
                          min_items=1,
                          max_items=1000),
     'remove_pos':  fields.List(fields.String(description='Needed POS'),
                                title="Remove POS from text using SpacyNLP library",
                                description="Remove Part Of Speech: list of possible tags can be found in SpacyNLP library website: 'https://spacy.io/api/annotation'",
                                required=False,
                                example=['ADP', 'ADV', 'AUX', 'CONJ', 'CCCONJ', 'DETTE', 'INTJ', 'NUM', 'PARTICAL', 'PRON', 'PUNCT', 'SCONJ', 'SYM', 'X']),
     'remove_stopwords':  fields.Boolean(description='Remove stopwords from the given text',
                                         title="Remove Stop Words",
                                         required=False,
                                         example=True,
                                         default=False),
     'lemmatize':  fields.Boolean(description='Give the lemmatized version of the text',
                                  title="Lemmatize text",
                                  required=False,
                                  example=True,
                                  default=False),
     'phrase':  fields.String(description='Give the phrased version of the text',
                               title="Phrase text",
                               required=False,
                               choices=['x5gon','wikipedia', False],
                               example=False,
                               default=False),
     'lowercase':  fields.Boolean(description='Give the lowercase version of the text',
                                  title="Lowercase text",
                                  required=False,
                                  example=True,
                                  default=False),
     'dfxp2text':  fields.Boolean(description='Give the text version of the dfxp input text',
                                  title="Dfxp to text",
                                  required=False,
                                  example=False,
                                  default=False)
    })


# Wikifification input model
input_def_tfidf_fetch = ("input_def_tfidf_fetch", {
    'resource_ids':  fields.List(fields.Integer(description='Instance id'),
                                 title="List of resources ids",
                                 description="An Integer list of resource ids in the project Database",
                                 required=True,
                                 example=[39435, 39426, 39425, 38657],
                                 min_items=1,
                                 max_items=1000),
     'tfidf_type':  fields.String(description='tfidf type string',
                             title="tfidf type",
                             required=True,
                             example="SIMPLE",
                             default="SIMPLE")
})

# Wikifification input model
input_def_wikification_fetch = ("input_def_wikification_fetch", {
    'resource_ids':  fields.List(fields.Integer(description='Instance id'),
                                 title="List of resources ids",
                                 description="An Integer list of resource ids in the project Database",
                                 required=True,
                                 example=[39435, 39426, 39425, 38657],
                                 min_items=1,
                                 max_items=1000),
     'wikification_type':  fields.String(description='Wikification type string',
                             title="Wikification type",
                             required=True,
                             example="SIMPLE",
                             default="SIMPLE")
})

# Wikification input model (compute from texts...)
input_def_wikification_text = ("input_def_wikification_text", {
    'resource_texts':  fields.List(fields.String(description='Instance text'),
                                   title="List of resources texts",
                                   description="A texts list",
                                   required=True,
                                   example=["Go play away...", "Go play away..."],
                                   min_items=1,
                                   max_items=1000),
    'wikification_type':  fields.String(description='Wikification type string',
                            title="Wikification type",
                            required=True,
                            example="SIMPLE",
                            default="SIMPLE")
})


# General input model (compute from texts...)
input_def_texts = ("input_def_texts", {
    'resource_texts':  fields.List(fields.String(description='Instance text'),
                                   title="List of resources texts",
                                   description="A texts list",
                                   required=True,
                                   example=["Go play away...", "Go play away..."],
                                   min_items=1,
                                   max_items=1000)
})


# Knn input model
input_def_knn_res = ("input_def_knn_res", {
    'resource_id': fields.Integer(description='Concerned resource id',
                                  title="Concerned resource",
                                  required=True,
                                  example=65478),
    'n_neighbors': fields.Integer(description='Number of needed neighbors',
                                  title="Number of needed neighbors",
                                  required=True,
                                  example=20,
                                  default=20)
})

input_def_knn_vect = ("input_def_knn_vect", {
    'vector': fields.Raw('dict',
                         description='Concerned vector',
                         title="Concerned vector",
                         required=True,
                         example={'key1': 'value1',
                                  'key2': 'value2'}),
    'n_neighbors': fields.Integer(description='Number of needed neighbors',
                                  title="Number of needed neighbors",
                                  required=True,
                                  example=20,
                                  default=20)
})

input_def_knn_vect_doc2vec = ("input_def_knn_vect_doc2vec", {
    'vector': fields.List(fields.Float,
                          title="Doc2vec vector",
                          description="Vector of 300 elements.",
                          required=True,
                          example=[2.0327847003936768, -0.5983495712280273, -0.23338322341442108, 0.3602330982685089],
                          min_items=300,
                          max_items=300),
    'n_neighbors': fields.Integer(description='Number of needed neighbors',
                                  title="Number of needed neighbors",
                                  required=True,
                                  example=20,
                                  default=20)
})

input_def_knn_text = ("input_def_knn_text", {
    'text': fields.String(description='A given plain text',
                                  title="Concerned text",
                                  required=True,
                                  example="Go play away..."),
    'n_neighbors': fields.Integer(description='Number of needed neighbors',
                                  title="Number of needed neighbors",
                                  required=True,
                                  example=20,
                                  default=20)
})

input_def_knn_text = ("input_def_knn_text", {
    'resource_text': fields.String(description='A given plain text',
                                  title="Concerned text",
                                  required=True,
                                  example="Go play away..."),
    'n_neighbors': fields.Integer(description='Number of needed neighbors',
                                  title="Number of needed neighbors",
                                  required=True,
                                  example=20)
})
# Lamdsh gettranscription input model
input_def_lamdshtrans = ("input_def_lamdshtrans", {
    'resource': fields.Integer(description='Concerned resource id',
                               title="Concerned resource",
                               required=True,
                               example=65478),
    'langorig': fields.String(description='Original language of the concerned resource id',
                              title="Original language of the concerned resource",
                              required=True,
                              example="fr",
                              default="fr")
})

# Lamdsh search input model (fetch ...)
input_def_lamdshsearch = ("input_def_lamdshsearch", {
    'search': fields.String(description='Search string',
                            title="Search string",
                            required=True,
                            example="grammatical",
                            default="grammatical")
})

# moodle playlist2mbz input model
input_def_mdlplaylist2mbz = ("input_def_mdlplaylist2mbz", {
    'playlist_general_infos': fields.Raw('dict',
                                         description='Playlist meta infos',
                                         title="Playlist general infos",
                                         required=True,
                                         example={"pst_name": "Machine learning",
                                                  "pst_id": "5645",
                                                  "pst_url": "x5learn.org/playlist/plst5645",
                                                  "pst_author": "Pr. Colin de la Higuera",
                                                  "pst_creation_date": "2020-03-25",
                                                  "pst_thumbnail_url": "",
                                                  "pst_description": "This a machine learning playlist",
                                                  "pst_license": "CC-BY"}),
     'playlist_items': fields.List(fields.Raw('dict'),
                          description='Playlist items',
                          title="Playlist items",
                          required=True,
                          example=[{ "url": "http://campus.unibo.it/78847/1/Statua%20del%20GUIDARELLO%20-%20La%20diagnostica.pdf",
                      	             "material_id": "4332",
                                     "x5gon_id": "4332",
                      	             "title": "Statua del GUIDARELLO - La diagnostica",
                      	             "provider": "University of Bologna Digital Library",
                      	             "description": "",
                      	             "date": "2012-3-26",
                      	             "duration": "30 mins",
                      	             "images": "",
                      	             "mediatype": "pdf",
                      	             "thumnail_url": "",
                      				 "order": "0"
                          			},{
                      			     "url": "https://ocw.mit.edu/courses/engineering-systems-division/esd-342-network-representations-of-complex-engineering-systems-spring-2010/lecture-notes/MITESD_342S10_lec01.pdf",
                      	             "material_id": "14806",
                                     "x5gon_id": "14806",
                      	             "title": "Network Representations of Complex Engineering Systems",
                      	             "provider": "MIT OpenCourseWare",
                      	             "description": "This course provides a deep understanding of engineering systems at a level intended for research on complex engineering systems. It provides a review and extension of what is known about system architecture and complexity from a theoretical point of view while examining the origins of and recent developments in the field. The class considers how and where the theory has been applied, and uses key analytical methods proposed. Students examine the level of observational (qualitative and quantitative) understanding necessary for successful use of the theoretical framework for a specific engineering system. Case studies apply the theory and principles to engineering systems.",
                      	             "date": "2012-3-26",
                      	             "duration": "20 mins",
                      	             "images": "",
                      	             "mediatype": "pdf",
          							 "thumnail_url": "",
          							 "order": "1"
                      				},{
                      				 "url": "http://hydro.ijs.si/v009/e3/4mwzlfru2g4bah6hpwdto5io5w6zztlu.mp4",
                      	             "material_id": "80539",
                                     "x5gon_id": "80539",
                      	             "title": "Pursuing The Endless Frontier: Essays on MIT and the Role of Research Universities",
                      	             "provider": "Videolectures.NET",
                      	             "description": "At the conclusion of 14 years at the helm of the Institute, Chuck Vest discusses the challenges and opportunities involved in guiding a major research university through tumultuous times. Vest’s new book, outlined in his remarks, provides a detailed and intimate view of his MIT “adventure.” Some key chapters: At the start of his tenure, he confronted a fundamental shift in the relationship between MIT and the federal government, driven by suspicion and hostility toward scientific research. He recognized the explosive growth and signal importance of such fields as molecular biology, neuroscience, and information technologies, and sought to deepen MIT’s investment in them.",
                      	             "date": "2012-3-26",
                      	             "duration": "60 mins",
                      	             "images": "",
                      	             "mediatype": "mp4",
          							 "thumnail_url": "",
          							 "order": "2"
                      				}
                              ]),
     'playlist_format': fields.String(description='Playlist infos format',
                             title="playlist format",
                             required=False,
                             example="mbz",
                             default="mbz")
})

# moodle x5plgnfreacs input model
input_def_mdlx5gnfreacs = ("input_def_mdlx5gnfreacs", {
    'x5gonValidated': fields.String(description='Date', title="Date", required=True, example="true", default="true"),
    'dt': fields.String(description='Date', title="Date", required=True, example="2020-05-14T11:52:11Z", default="2020-05-14T11:52:11Z"),
    'rq': fields.String(description='Request url', title="Request url", required=True, example="http://localhost:8080/moodle3p6/mod/xfgon/discovery.php?id=405", default="http://localhost:8080/moodle3p6/mod/xfgon/discovery.php?id=405"),
    'rf': fields.String(description='Referer url', title="Referer url", required=True, example="http://localhost:8080/moodle3p6/mod/xfgon/view.php?id=405", default="http://localhost:8080/moodle3p6/mod/xfgon/view.php?id=405"),
    'cid': fields.String(description='Provider token', title="Provider token", required=True, example="x5gonPartnerToken", default="x5gonPartnerToken"),
    'providertype': fields.String(description='Provider type', title="Provider type", required=True, example="", default="Machine learning activity"),
    'title': fields.String(description='Title', title="Title", required=True, example="moodle", default="moodle"),
    'description': fields.String(description='Description', title="Description", required=True, example="Machine learning activity", default="Machine learning activity"),
    'author': fields.String(description='Author', title="Author", required=True, example="", default=""),
    'language': fields.String(description='Language', title="Language", required=True, example="", default=""),
    'creation_date': fields.String(description='Creation date', title="Creation date", required=True, example="1588858739", default="1588858739"),
    'type': fields.String(description='Type', title="Type", required=True, example="xfgon", default="xfgon"),
    'mimetype': fields.String(description='mimetype', title="mimetype", required=True, example="", default=""),
    'license': fields.String(description='license', title="license", required=True, example="", default=""),
    'licensename': fields.String(description='licensename', title="licensename", required=True, example="", default=""),
    'resurl': fields.String(description='Resourse url', title="Resourse url", required=True, example="http://localhost:8080/moodle3p6/mod/xfgon/discovery.php?id=405", default="http://localhost:8080/moodle3p6/mod/xfgon/discovery.php?id=405"),
    'resmdlid': fields.String(description='Resourse mdl id', title="Resourse mdl id", required=True, example="405", default="405"),
    'residinhtml': fields.String(description='Resourse mdl id in page', title="Resourse mdl id in page", required=True, example="", default=""),
    'resurlinpage': fields.String(description='Resourse mdl url in page', title="Resourse mdl url in page", required=True, example="http://localhost:8080/moodle3p6/mod/xfgon/discovery.php?id=405", default="http://localhost:8080/moodle3p6/mod/xfgon/discovery.php?id=405"),
    'rescrstitle': fields.String(description='Course title', title="Course title", required=True, example="Machine Learning Level2", default="Machine Learning Level2"),
    'rescrsid': fields.String(description='Course id', title="Course id", required=True, example="2", default="2"),
    'rescrsurl': fields.String(description='Course url', title="Course url", required=True, example="http://localhost:8080/moodle3p6/course/view.php?id=2", default="http://localhost:8080/moodle3p6/course/view.php?id=2"),
    'rescrssum': fields.String(description='Course summary', title="Course summary", required=True, example="<p>Resources for MLearning</p>", default="<p>Resources for MLearning</p>"),
    'rescrslang': fields.String(description='Course language', title="Course language", required=True, example="", default=""),
    'rescrsctg': fields.String(description='Course category', title="Course category", required=True, example="OpenCourseWare", default="OpenCourseWare"),
    'rescrsctgdesc': fields.String(description='Course category desc', title="Course category desc", required=True, example="<p>Open courses</p>", default="<p>Open courses</p>"),
    'mdaccess': fields.String(description='Media access', title="Media access", required=True, example="no", default="no"),
    'mdaction': fields.String(description='Media action', title="Media action string", required=True, example="", default=""),
    'mdsrc': fields.String(description='Media src', title="Media src", required=True, example="", default=""),
    'mdduration': fields.String(description='Media duration', title="Media duration", required=True, example="", default=""),
    'mdactiontime': fields.String(description='Media action time', title="Media action time", required=True, example="", default=""),
    'freacs': fields.String(description='X5gon feature access', title="X5gon feature access", required=True, example="{\"fre\":\"x5discovery\",\"acttype\":\"search\",\"actdata\":{\"x5dq\":\"intelligent robots\"},\"timestamp\":\"1589457131259\"}", default="{\"fre\":\"x5discovery\",\"acttype\":\"search\",\"actdata\":{\"x5dq\":\"intelligent robots\"},\"timestamp\":\"1589457131259\"}")
    # 'freacs': fields.Raw('dict',
    #                      description='X5gon feature access',
    #                      title="X5gon feature access",
    #                      required=True,
    #                      example={"fre":"x5discovery","acttype":"search","actdata":{"x5dq":"intelligent robots"},"timestamp":"1589457131259"},
    #                      # default={"fre":"x5discovery","acttype":"search","actdata":{"x5dq":"intelligent robots"},"timestamp":"1589457131259"}
    #                      )
    })


# mdlx5gnfrepte search input model
input_def_mdlx5gnfrepte = ("input_def_mdlx5gnfrepte", {
    'fre': fields.String(description='X5 feature needed to be populated',
                           title="X5 feature",
                           required=True,
                           example="x5discovery",
                           default="x5discovery"),
    'max_pdres': fields.Integer(description='Number of proposed items',
                                title="Number of proposed items",
                                required=True,
                                example=10,
                                default=10),
    "grpgcrta": fields.Raw('dict',
                           description='Depending on which creteria, the group activities will be computed',
                           title="Grouping creteria",
                           required=True,
                           example={"name":"crsuri","value":"http://localhost:8080/moodle3p6/course/view.php?id=2"}),
    "grpgcrta_data": fields.Raw('dict',
                                description='Grouping creteria data',
                                title="Grouping creteria data",
                                required=True,
                                example={"crstitle":"Machine learning","crssummary":"ML is the art of the automatic learning","modtitle":"deep learning","modsummary":"small introduction for deep learning","customhint":"wonder about the different types of learning"})
                            })

input_def_mdlx5gnoeracs = ("input_def_mdlx5gnoeracs", {
    'fre': fields.String(description='X5 feature needed to be populated',
                           title="X5 feature",
                           required=True,
                           example="x5discovery",
                           default="x5discovery"),
    'max_pdres': fields.Integer(description='Number of proposed items',
                                title="Number of proposed items",
                                required=True,
                                example=10,
                                default=10),
    "grpgcrta": fields.Raw('dict',
                           description='Depending on which creteria, the group activities will be computed',
                           title="Grouping creteria",
                           required=True,
                           example={"name":"crsuri","value":"http://localhost:8080/moodle3p6/course/view.php?id=2"}),
    "grpgcrta_data": fields.Raw('dict',
                                description='Grouping creteria data',
                                title="Grouping creteria data",
                                required=True,
                                example={"crstitle":"Machine learning","crssummary":"ML is the art of the automatic learning","modtitle":"deep learning","modsummary":"small introduction for deep learning","customhint":"wonder about the different types of learning"}),
    'oers': fields.List(fields.Integer(description='Oer id'),
                        title="oers list",
                        required=False,
                        example=[1234, 56678, 56788],
                        min_items=0,
                        max_items=50)
                            })


# Modelsdsh search input model
input_def_modelsdshsearch = ("input_def_modelsdshsearch", {
    'q': fields.String(description='Search string',
                            title="Search string",
                            required=True,
                            example="grammatical inference",
                            default="grammatical inference"),
    'type': fields.List(fields.String(description='Resource type'),
                                  title="Resource type",
                                  description="Resource type",
                                  required=False,
                                  example=['mp4', 'docx', 'pdf'],
                                  min_items=0,
                                  max_items=10),
    'available_langs': fields.List(fields.String(description='Available languages'),
                                  title="List of available languages",
                                  description="String list of the short form of the needed available traslations",
                                  required=False,
                                  example=['en', 'fr', 'sl', 'ru'],
                                  min_items=0,
                                  max_items=10),
    'provider': fields.List(fields.Integer(description='Resource provider'),
                                  title="Resource provider",
                                  description="String list of the short form of the needed providers",
                                  required=False,
                                  example=[1, 2, 3, 4],
                                  min_items=0,
                                  max_items=10),
    'orig_lang': fields.List(fields.String(description='Resource original language'),
                                          title="List of original languages",
                                          description="A string list of the short form of the needed original languages",
                                          required=False,
                                          example=['fr', 'en', 'sl'],
                                          min_items=0,
                                          max_items=7),
    'max_resources': fields.Integer(description='Max number of resources to include in the page',
                                    required=False,
                                    default=20,
                                    example=20),
    'max_concepts': fields.Integer(description='Number of concepts/keywords to include in the results',
                                   required=False,
                                   default=20,
                                   example=20),

})

input_def_modelsdshneig = ("input_def_modelsdshneig", {
    'id': fields.Integer(description='Reference resource id',
                                  title="Concerned resource",
                                  required=True,
                                  example=65478),
    'max_resources': fields.Integer(description='Number of needed neighbors',
                                  title="Number of needed neighbors",
                                  required=True,
                                  example=20,
                                  default=20),
    'max_concepts': fields.Integer(description='Number of needed commun concepts',
                                  title="Number of needed commun concepts",
                                  required=True,
                                  example=20,
                                  default=20),
                            })


# Missingres input model
input_def_missingresource = ('input_def_missingresource', {
    'previous': fields.Integer(description='Previous resource id',
                               required=True,
                               example=39434),
    'after': fields.Integer(description='Next resource id',
                            required=True,
                            example=39499),
    'candidate_ids':  fields.List(fields.Integer(description='Resource id'),
                                  title="List of candidate resources ids",
                                  description="An Integer list of candidate resource ids in the Database",
                                  required=True,
                                  example=[39435, 39426, 39425, 38657],
                                  min_items=1,
                                  max_items=1000)
})

# Reordonize input model
input_def_reordonize = ('input_def_reordonize', {
    'resource_id':  fields.Integer(description='Concerned resource id',
                                   required=True,
                                   example=39420),
    'candidate_ids':  fields.List(fields.Integer(description='Resource id'),
                                  title="List of candidate resources ids",
                                  description="An Integer list of candidate resource ids in the Database",
                                  required=True,
                                  example=[39435, 39426, 39425, 38657],
                                  min_items=1,
                                  max_items=1000)
})

# RecommendV1 input model
input_def_recommend_v1 = ('input_def_update', {
    'resource_id': fields.Integer(description='Concerned resource id',
                                  title="Concerned resource",
                                  required=True,
                                  example=65478),
    'n_neighbors': fields.Integer(description='Number of needed neighbors',
                                  title="Number of needed neighbors",
                                  required=True,
                                  example=20,
                                  default=20),
    'remove_duplicates':  fields.Integer(title="Remove Duplicates",
                                      description="Remove duplicates or very similar resources",
                                      required=False,
                                      example=1),
    'model_type': fields.String(description='Knn model type',
                                title="Number of needed neighbors",
                                required=False,
                                example='doc2vec',
                                default='doc2vec')
})

# RecommendV1 input model
input_def_recommend_v1 = ('input_def_update', {
    'resource_id': fields.Integer(description='Concerned resource id',
                                  title="Concerned resource",
                                  required=True,
                                  example=65478),
    'n_neighbors': fields.Integer(description='Number of needed neighbors',
                                  title="Number of needed neighbors",
                                  required=True,
                                  example=20),
    'model_type': fields.String(description='Knn model type',
                                title="Number of needed neighbors",
                                required=False,
                                example='doc2vec')
})


# SearchV1 input model
input_def_searchv1 = ('input_def_searchv1', {
    'text':  fields.String(title="Text",
                           description="Search string",
                           required=True,
                           example='machine learning applied on health sector'),
    'type': fields.String(description='Resources type you want to receive',
                          title="Resources type",
                          required=False,
                          example="pdf"),
    'page': fields.Integer(description='Results page number',
                           title="Results page number",
                           required=False,
                           example=1),
    'model_type':  fields.String(title="Knn model type",
                                 description="Based on which knn model, search will be executed",
                                 required=False,
                                 example='doc2vec'),
})

# SearchV1 input model
input_def_searchv1 = ('input_def_searchv1', {
    'text':  fields.String(title="Text",
                           description="Search string",
                           required=True,
                           example='machine learning applied on health sector'),
    'type': fields.String(description='Resources type you want to receive',
                          title="Resources type",
                          required=False,
                          example="pdf"),
    'page': fields.Integer(description='Results page number',
                           title="Results page number",
                           required=False,
                           example=1),
    'model_type':  fields.String(title="Knn model type",
                                 description="Based on which knn model, search will be executed",
                                 required=False,
                                 example='doc2vec'),
    'remove_duplicates':  fields.Integer(title="Remove Duplicates",
                                      description="Remove duplicates or very similar resources",
                                      required=False,
                                      example=1),
    'nb_wikiconcepts':  fields.Integer(title="Number of Wikipedia concepts",
                                       description="Number of needed Wikipedia concepts",
                                       required=False,
                                       example=5),
    'return_wikisupport':  fields.Integer(title="Return wikipedia support",
                                       description="Specify either to return support or not in wikipedia concepts",
                                       required=False,
                                       example=0)
})

input_def_update = ('input_def_update', {
    'model':  fields.String(title="Path to model",
                            description="the path to the target model",
                            required=True,
                            example='x5gonwp3models/models/tool_name/model/default'),
    'resume': fields.Integer(description='Resume the update or compute from the beginning: "1" for resuming',
                             title="Resume parameter",
                             required=True,
                             example=0),
    'exp_id': fields.Integer(description='Experiment Id',
                             title="Experiemnt ID",
                             required=True,
                             example=0)
})

input_def_basket = ('input_def_basket_to_sequence', {
    'basket':  fields.List(fields.Integer(description='Instance id'),
                           title="List of resources ids",
                           description="An Integer list of resource ids in the project Database",
                           required=True,
                           example=[87727, 87744, 87725, 87729, 87724, 87736],
                           min_items=1,
                           max_items=1000),
    'order_model': fields.String(title="order model",
                                 description="order model type",
                                 required=False,
                                 example='rnn2order',
                                 default='rnn2order')
})



input_def_insert_in_sequence = ('input_def_insert_in_sequence', {
    'sequence':  fields.List(fields.Integer(description='Instance id'),
                             title="List of resources ids",
                             description="An Integer list of resource ids in the project Database",
                             required=True,
                             example=[87724, 87727, 87729, 87725, 87736, 87744],
                             min_items=1,
                             max_items=1000),
    'max_concepts':fields.Integer(description='max number of returned concepts',
                                  default=20,
                                  required=False,
                                  example=20),
    'order_model': fields.String(title="order model",
                                 description="order model type",
                                 required=False,
                                 example='rnn2order',
                                 default='rnn2order')
})

input_def_sequence = ('input_def_sequence', {
    'sequence':  fields.List(fields.Integer(description='Instance id'),
                             title="List of resources ids",
                             description="An Integer list of ordered resource ids in the project Database",
                             required=True,
                             example=[87724, 87727, 87729, 87725, 87736, 87744],
                             min_items=1,
                             max_items=1000)
})


input_def_generation = ('input_def_generation', {})

# Output Models
# General output model
output_def = ("output_def", {
    # 'output': fields.Raw('dict')
    'output': fields.Raw('dict',
                         description='Output vector usually in list format (batch of resources/texts)',
                         title="Output vector",
                         required=True,
                         example='{...}')
})
# Output model for modelsdsh search service:
output_def_modelsdshsearch = ("output_def_modelsdshsearch", {
                              'result': fields.List(fields.Raw('dict',
                                                   description='search result infos',
                                                   title="Search result infos",
                                                   required=True,
                                                   example=''))})

output_def_modelsdshneig = ("output_def_modelsdshneig", {
                              'reference': fields.Raw('dict',
                                                   description='Reference resource infos',
                                                   title="Reference resource infos",
                                                   required=True,
                                                   example=''),
                              'neighbors': fields.List(fields.Raw('dict',
                                                   description='Neighbors to reference resource infos',
                                                   title="Neighbors to reference resource infos",
                                                   required=True,
                                                   example=''))})

# Output model for RS/Recommend V1 services:
output_def_rsrecommend = ("output_def_rsrecommend", fields.Raw('dict',
                         description='Output vector usually in list format (batch of resources/texts)',
                         title="Output vector",
                         required=True,
                         example='{...}')
)

# Outout model for the ordering of multiple ressources
output_def_ordered_resources = ("output_def_ordered_resources", {
    "output": fields.List(fields.Integer(description='Instance id'),
                          title="List of resources ids",
                          description="An ordered Integer list of resource ids",
                          required=True,
                          example=[39435, 39426, 39425, 38657],
                          min_items=1,
                          max_items=1000)})

sequence_distance = {"sequence": fields.List(fields.Integer(description='Instance id'),
                                             title="Ordered list of resources ids",
                                             description="An ordered Integer list of resource ids",
                                             required=True,
                                             example=[39435, 39425, 39426, 38657],
                                             min_items=1,
                                             max_items=1000),
                     "distances": fields.List(fields.Float,
                                              title="Distances between resources",
                                              description="Distances between consecutive resources in the sequence",
                                              required=True,
                                              example=[0.1, 0.2, 0.3, 0.4],
                                              min_items=0,
                                              max_items=1000)}

# Outout model for the creation of a sequence
output_def_sequence_distance = ("output_def_sequence_distance", {
    "output": fields.Nested(sequence_distance)})

# Outout model for the creation of a sequence
output_def_sequence_distance = ("output_def_sequence_distance", {
    "output": fields.Nested(sequence_distance)})

# Output model for user data generation services:
output_def_generation = ("output_def_generation", fields.Raw('dict',
                         description='',
                         title="",
                         required=True,
                         example=''))

# Output model for playlist2mbz
output_def_moodleplaylist2mbz = ("output_def_moodleplaylist2mbz",
        {"output": fields.Raw('dict',
                         description='',
                         title="",
                         example='{}')})

#  Output model for mdlx5gnfreacs
output_def_mdlx5gnfreacs = ("output_def_mdlx5gnfreacs", {
    # 'result': fields.String(description='Action result',
    #                         title="Action result",
    #                         required=True,
    #                         example='success',
    #                         default='success'),
    # 'actions': fields.String(description='Post request action',
    #                          title="Post request action",
    #                          required=False,
    #                          example='update',
    #                          default=''),
    # # 'pddata': fields.Raw('dict',
    #                  description='',
    #                  title="",
    #                  example='{}'),
    "output": fields.Raw('dict',
                     description='',
                     title="",
                     example='{}')
})

#  Output model for mdlx5gnfrepte
output_def_mdlx5gnfrepte = ("output_def_mdlx5gnfrepte", {
    'result': fields.String(description='Action result',
                            title="Action result",
                            required=True,
                            example='success',
                            default='success'),
    'actions': fields.String(description='Post request action',
                             title="Post request action",
                             required=False,
                             example='update',
                             default=''),
    'pddata':  fields.Raw('dict',
                          description='Proposed data by the recommendation group algorithms',
                          title="Proposed data",
                          example='{}')
    # "output": fields.Raw('dict',
    #                  description='',
    #                  title="",
    #                  example='{}')
})

output_def_mdlx5gnoeracs = ("output_def_mdlx5gnoeracs", {
    'result': fields.String(description='Action result',
                            title="Action result",
                            required=True,
                            example='success',
                            default='success'),
    'actions': fields.String(description='Post request action',
                             title="Post request action",
                             required=False,
                             example='update',
                             default=''),
    'pddata':  fields.Raw('dict',
                          description='Proposed data by the recommendation group algorithms',
                          title="Proposed data",
                          example='{}')

})
