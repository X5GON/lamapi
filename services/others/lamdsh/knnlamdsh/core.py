from components.dataconnection.index import *
from services.distance.doc2vec.knn.core import knn_doc2vec_res
from services.distance.wikifier.knn.core import knn_wikifier_res
from services.distance.text2tfidf.knn.core import knn_tfidf_res

from collections import Counter


def get_knn_resourcesmetadata(parameters):
    tmp_parameters = {}
    tmp_parameters["resource_id"] = parameters['resource_id']
    tmp_parameters["n_neighbors"] = parameters['n_neighbors']
    tmp_parameters["remove_duplicates"] = parameters['remove_duplicates']
    tmp_parameters["return_reduction"] = True
    tmp_parameters["return_matrix"] = True
    tmp_parameters["return_vectors"] = True
    tmp_parameters["return_dist"] = True
    if parameters["model_type"] == 'tfidf':
        knn = knn_tfidf_res(**tmp_parameters)
    elif parameters["model_type"] == 'wikifier':
        knn = knn_wikifier_res(**tmp_parameters)
    elif parameters["model_type"] == 'doc2vec':
        knn = knn_doc2vec_res(**tmp_parameters)
    # Get the concepts
    if parameters["model_type"] == 'wikifier':
        conceptsmax = Counter()
        concetpsmostcommon = Counter()
        for v in knn["vectors"]:
            conceptsmax += Counter(v)
            concetpsmostcommon += Counter(v.keys())
        sumpr = sum(conceptsmax.values())
    resource_id = knn["resource_id"]
    matrix = knn["matrix"]
    projected_matrix = knn["projected_matrix"]
    all_neig = fetch_resources_datafromdb_forlamdash(knn=knn)
    a = {
             "res_in_focus": all_neig[int(resource_id)],
             "neighbors": list(all_neig.values()),
             "matrix": matrix,
             "top": knn["top"],
             "distances": knn["distances"],
             "projected_matrix": projected_matrix,
             "metrics_limits": get_metrics_bounds_forlamdash(all_neig),
             "concepts_max": [(c, v/sumpr) for c, v in conceptsmax.most_common(10)] if parameters["model_type"] =='wikifier' else None,
             "nb_concepts": len(conceptsmax) if parameters["model_type"] =='wikifier' else None,
             "distri": list(conceptsmax.items()) if parameters["model_type"] =='wikifier' else None,
             "concepts_most_common": concetpsmostcommon.most_common(10) if parameters["model_type"] =='wikifier' else None,
             "variance_ratio_": knn["variance_ratio_"].tolist() if knn["variance_ratio_"] is not None else None
           }
    return a
