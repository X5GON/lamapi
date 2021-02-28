from components.dataconnection.index import get_resource_description
from services.distance.wikifier.knn.core import knn_wikifier_res
from x5gonwp3tools.tools.difficulty.difficulty import __wpm, wikification2con_per_sec, tfidf2technicity

import datetime
from collections import Counter

from SETTINGS import EXP_IDS


def get_resource_modelsdshknn(parameters):
    # max_concepts
    tmp_parameters = {}
    tmp_parameters["resource_id"] = parameters['id']
    tmp_parameters["n_neighbors"] = parameters['max_resources']
    tmp_parameters["remove_duplicates"] = True
    tmp_parameters["return_reduction"] = True
    tmp_parameters["return_matrix"] = True
    tmp_parameters["return_vectors"] = True
    tmp_parameters["return_dist"] = True
    # Get Knn resources
    knn = knn_wikifier_res(**tmp_parameters)
    resources_ids = knn["neighbors"]
    matrix = knn["matrix"]
    # Get resources descriptions
    resources_needed_infos = get_resource_description(resources_ids,
                                                      {"concepts": EXP_IDS['wikifier']['SIMPLE']['experiment_id'],
                                                       "keywords": EXP_IDS['text2tfidf']['SIMPLE']['experiment_id']},
                                                      max_concepts=parameters['max_concepts'],
                                                      max_keywords=parameters['max_concepts'])
    # Get the concepts
    conceptsmax = Counter()
    concetpsmostcommon = Counter()
    for v in knn["vectors"]:
        conceptsmax += Counter(v)
        concetpsmostcommon += Counter(v.keys())
    sumpr = sum(conceptsmax.values())
    # Get the most common concepts
    most_common_concepts = [(c, v/sumpr) for c, v in conceptsmax.most_common(parameters['max_concepts'])]
    # Fill up the missings needed infos: ContextualResourceDescription
    resources_final_infos = []
    for i, rid in enumerate(resources_ids):
        res_infos = resources_needed_infos.get(int(rid), dict())
        if res_infos:
            res_infos['duration'] = 60 * (res_infos['len_word'] / __wpm()["Slide"])
            res_infos['difficulty'] = wikification2con_per_sec(res_infos['len_char'], res_infos['len_concepts'])
            # res_infos['difficulty'] = tfidf2technicity( res_infos['keywords_full'] )
            res_infos['projection'] = knn["projected_matrix"][i]
            common_wk_in_res = [[dict(label= c_f["title"],
                                                  url=  c_f["url"],
                                                  value= c_f["norm_pageRank"]) for c_f in filter(lambda c_res: c_res['url'] == c,
                                                                                                 res_infos["wikifier_full"]["value"]["concepts"])]
                                            for c, v_c in most_common_concepts]
            res_infos['common_wikifier'] = [c[0] for c in common_wk_in_res if len(c) > 0]
            res_infos['distance'] = knn["distances"][i]
            del res_infos['keywords_full']
            del res_infos['wikifier_full']
        resources_final_infos.append(res_infos)
    a = {
             "reference": resources_final_infos[0],
             "neighbors": resources_final_infos[1:],
             # "matrix": matrix,
             # "top": knn["top"],
             # "distances": knn["distances"],
             # "concepts_max": [(c, v/sumpr) for c, v in conceptsmax.most_common(10)],
             # "distri": list(conceptsmax.items()),
             # "concepts_most_common": concetpsmostcommon.most_common(10),
             # "variance_ratio_": knn["variance_ratio_"].tolist() if knn["variance_ratio_"] is not None else None
           }
    return a
