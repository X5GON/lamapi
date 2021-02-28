from services.distance.wikifier.knn.core import knn_wikifier_res
from services.distance.doc2vec.knn.core import knn_doc2vec_res
from services.distance.text2tfidf.knn.core import knn_tfidf_res
from components.dataconnection.index import get_experimental_metadatas, get_experimental_features
from SETTINGS import EXP_IDS

from utils import time_usage


# Get resTrans for lamdsh
def get_resource_recommend_v1(model_type="wikifier", **kwargs):
    if model_type == "wikifier":
        res = knn_to_x5gon_outputformat(knn_neighbors=knn_wikifier_res(return_dist=True, **kwargs))
    if model_type == "doc2vec":
        res = knn_to_x5gon_outputformat(knn_neighbors=knn_doc2vec_res(return_dist=True, **kwargs))
    if model_type == "tfidf":
        res = knn_to_x5gon_outputformat(knn_neighbors=knn_tfidf_res(return_dist=True, **kwargs))
    del res[kwargs["resource_id"]]
    return {"rec_materials": list(res.values())}


@time_usage
def knn_to_x5gon_outputformat(knn_neighbors, return_wikisupport=False):
    resources_ids = knn_neighbors['neighbors']
    resources_distances = knn_neighbors['distances']
    neighbors_metadata = get_experimental_metadatas(resource_ids=knn_neighbors['neighbors'])
    neighbors_features = get_experimental_features(resource_ids=knn_neighbors['neighbors'], experiment_ids=[EXP_IDS['wikifier']['FULL']['experiment_id']])
    rec_materials = {}
    # Intialize to garantee to return all the resources
    idx = 0
    for rid in resources_ids:
        rec_materials[rid] = dict(material_id=rid,
                                  weight=resources_distances[idx],
                                  url='',
                                  title='',
                                  description='',
                                  provider='',
                                  language='',
                                  type='',
                                  wikipedia=[])
        idx += 1
    # Get all possible resources metadata
    for res in neighbors_metadata:
        # print(res)
        rid = res["id"]
        resource_info = rec_materials.get(rid, {})
        resource_info.update(**dict(material_id=res["id"],
                                    url=res["url"],
                                    title=res["title"],
                                    description=res["description"],
                                    provider=res["provider"],
                                    language=res["language"],
                                    type=res["type"],
                                    ))
    # Get wikipedia concepts
    for res in neighbors_features:
        rid = res["id"]
        resource_info = rec_materials.get(rid, {})
        resource_info.update(**dict(wikipedia=[dict(title=sres["title"],
                                                url=sres["url"],
                                                pageRank=sres["pageRank"],
                                                cosine=sres["cosine"],
                                                support=sres["support"] if return_wikisupport else None
                                                ) for sres in res["result"]['value']["concepts"]]
                                   ))
    return rec_materials
