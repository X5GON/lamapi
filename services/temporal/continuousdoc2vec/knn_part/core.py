from components.dataconnection.index import (get_experimental_features)
from sklearn.metrics import pairwise_distances

from x5gonwp3models.modelloader import load_model
from x5gonwp3tools.tools.continuousdoc2vec.continuousdoc2vec import __interpolate
from SETTINGS import EXP_IDS
from utils import dimension_reduction, filter_knn

# Get knn_doc2vec model from the global SETTINGS: 'dcknlt'=latestDoc2vecKnnModel
# knnmodel = load_model('dcknlt')
experiment_id = EXP_IDS['continuousdoc2vec']['V1']['experiment_id']

def knn_doc2vec_vect(vector, **kwargs):
    res = __knn_continuousDoc2vec(resource_vector=vector, **kwargs)
    res.update(vector=vector)
    return res


def knn_doc2vec_text(resource_text, **kwargs):
    vec = __interpolate(resource_text, model=load_model('ccmllt'))
    return __knn_doc2vec(resource_vector=vec, **kwargs)


def __knn_continuousDoc2vec(part_vector,
                            n_neighbors=20,
                            return_vectors=False,
                            return_dist=False,
                            resource_id=None):
    model=load_model('ccknlt')[0]
    ids=load_model('ccknlt')[1]
    dists, neigh_index = model.kneighbors([resource_vector], return_distance=True, n_neighbors=int(n_neighbors))
    dists = dists.tolist()[0]
    neigh_partids = (ids["index2id"][i] for i in neigh_index[0])
    neigh_ids = {}
    for partid in neigh_partids:
        rid, partid = partid.split("p")
        neigh_ids[rid] = neigh_ids.get(rid, []) + partid

    if return_vectors:
        vectors = [resource_vector]
        gen = get_experimental_features(list(neigh_ids.keys()),
                                        [experiment_id],
                                        order_needed=False)
        for d in gen:
            rid = d["id"]
            for part_id in neigh_ids[d["id"]]:
                dvect[f"{rid}p{part_id}"] = d["result"]["value"][part_id]
        for rid in neigh_ids:
            vectors.append(dvect[rid])
    return {
            "neighbors": neigh_ids,
            "distances": dists if return_dist else None,
            "vectors": vectors if return_vectors else None,
            }
