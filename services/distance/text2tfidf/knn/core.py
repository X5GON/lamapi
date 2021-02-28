from components.dataconnection.index import get_experimental_features
from scipy.sparse import dok_matrix, vstack
from sklearn.metrics import pairwise_distances

import numpy as np
from x5gonwp3models.modelloader import load_model
from x5gonwp3tools.tools.text2tfidf.tfidf import interpolates
from SETTINGS import EXP_IDS
from utils import dimension_reduction, filter_knn, time_usage

# Get knn_tfidf model from the global SETTINGS: 'wrknlt'=latesttfidfKnnModel
# knnmodel = load_model('tfknlt[1-2]-grams')
# model = load_model('tfmllt[1-2]-grams')
experiment_id = EXP_IDS['text2tfidf']['[1-2]-grams']['experiment_id']


def knn_tfidf_res(resource_id, **kwargs):
    tfidf = next(get_experimental_features([resource_id], [experiment_id]))["result"]["value"]
    res = __knn_tfidf(resource_tfidf=tfidf,
                      resource_id=resource_id,
                      **kwargs)
    res.update(resource_id=resource_id)
    return res


def knn_tfidf_vect(vector, **kwargs):
    res = __knn_tfidf(resource_tfidf=vector, **kwargs)
    res.update(vector=vector)
    return res


def knn_tfidf_text(resource_text, **kwargs):
    tfidf = interpolates([resource_text], load_model('tfmllt[1-2]-grams'), return_format="dict")[0]
    return __knn_tfidf(resource_tfidf=tfidf, **kwargs)


@time_usage
def __knn_tfidf(resource_tfidf,
                n_neighbors=20,
                return_reduction=False,
                return_vectors=False,
                return_dist=False,
                return_matrix=False,
                reduction_type="TruncatedSVD",
                remove_duplicates=False,
                resource_id=None):
    keyword_map = load_model('tfknlt[1-2]-grams')[2]
    model = load_model('tfknlt[1-2]-grams')[0]
    ids = load_model('tfknlt[1-2]-grams')[1]
    # print(type(keyword_map), type(model), type(ids))
    # print(keyword_map.keys())
    top = None
    resource_vector = dok_matrix((1, len(keyword_map["index2keyword"])),
                                 dtype=np.float32)
    keyword_not_found = 0
    for k, v in resource_tfidf.items():
        try:
            ind = keyword_map["keyword2index"][k]
            resource_vector[0, ind] = v
        except KeyError:
            keyword_not_found += 1
    dists, neigh_index = model.kneighbors(resource_vector,
                                          n_neighbors=n_neighbors,
                                          return_distance=True)
    dists = dists.tolist()[0]
    neigh_ids = [ids["index2id"][i] for i in neigh_index[0]]

    if resource_id is not None and remove_duplicates:
        dists, neigh_ids = zip(*((d, oerid) for d, oerid in zip(dists, neigh_ids) if d > 1e-4 or oerid  == resource_id))
    if return_vectors or return_matrix or return_reduction or remove_duplicates:
        gen = get_experimental_features(neigh_ids, [experiment_id],
                                        order_needed=False)
        neighbors_tfidf = {d["id"]: d["result"]["value"] for d in gen}
        neighbors_vector = dok_matrix((len(neighbors_tfidf), len(keyword_map["index2keyword"])),
                                      dtype=np.float32)
        for i, rid in enumerate(neigh_ids):
            for k, v in neighbors_tfidf[rid].items():
                ind = keyword_map["keyword2index"][k]
                neighbors_vector[i, ind] = v
        vectors = vstack((resource_vector, neighbors_vector))
        # print(type(vectors))
    if return_matrix or return_reduction or remove_duplicates:
        matrix = pairwise_distances(vectors, metric="cosine")
    if remove_duplicates:
        matrix, vectors, dists, neigh_ids = filter_knn(matrix,
                                                       vectors,
                                                       dists,
                                                       neigh_ids)
    if return_reduction:
        reductor = dimension_reduction(reduction_type, vectors.shape[0] - 1)
        matrix_projected = reductor.fit_transform(vectors)
        print(reductor.components_.shape)
        top = []
        for i in range(reductor.components_.shape[0]):
            top_ = sorted(enumerate(reductor.components_[i].tolist()), key=lambda x: x[1], reverse=True)
            top_ = map(lambda x: (keyword_map["index2keyword"][x[0]], x[1]), top_)
            top_ = list(filter(lambda x: x[1] != 0, top_))
            top.append(top_)
    if return_vectors:
        json_vectors = [{} for _ in range(vectors.shape[0])]
        for k, v in vectors.todok().items():
            json_vectors[k[0]][keyword_map["index2keyword"][k[1]]] = float(v)
    return {"neighbors": neigh_ids,
            "keyword_not_found": keyword_not_found,
            "distances": dists if return_dist else None,
            "vectors": json_vectors if return_vectors else None,
            "matrix": matrix.tolist() if return_matrix else None,
            "projected_matrix": matrix_projected.tolist() if return_reduction else None,
            "top": top,
            "variance_ratio_": reductor.explained_variance_ratio_ if return_reduction and\
                                                                     (reduction_type=="PCA" or\
                                                                      reduction_type=="TruncatedSVD" or\
                                                                      reduction_type=="SparsePCA"
                                                                     ) else None
         }
