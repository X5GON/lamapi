from components.dataconnection.index import (get_experimental_features)
from sklearn.metrics import pairwise_distances

from x5gonwp3models.modelloader import load_model
from x5gonwp3tools.tools.doc2vec.doc2vec import __interpolate
from SETTINGS import EXP_IDS
from utils import dimension_reduction, filter_knn

# Get knn_doc2vec model from the global SETTINGS: 'dcknlt'=latestDoc2vecKnnModel
# knnmodel = load_model('dcknlt')
experiment_id = EXP_IDS['doc2vec']['V1']['experiment_id']


def knn_doc2vec_res(resource_id, **kwargs):
    vec = next(get_experimental_features([resource_id], [experiment_id]))["result"]["value"]
    res = __knn_doc2vec(resource_vector=vec,
                        resource_id=resource_id,
                        **kwargs)
    res.update(resource_id=resource_id)
    return res


def knn_doc2vec_vect(vector, **kwargs):
    res = __knn_doc2vec(resource_vector=vector, **kwargs)
    res.update(vector=vector)
    return res


def knn_doc2vec_text(resource_text, **kwargs):
    vec = __interpolate(resource_text, model=load_model('dcmllt'))
    return __knn_doc2vec(resource_vector=vec, **kwargs)


def __knn_doc2vec(resource_vector,
                  n_neighbors=20,
                  return_reduction=False,
                  return_vectors=False,
                  return_dist=False,
                  return_matrix=False,
                  reduction_type="PCA",
                  remove_duplicates=False,
                  resource_id=None):
    knnmodel = load_model('dcknlt')
    model = knnmodel[0]
    # model.set_params(n_jobs=1)
    # print(model.get_params())
    ids = knnmodel[1]
    dists, neigh_index = model.kneighbors([resource_vector], return_distance=True, n_neighbors=int(n_neighbors))
    dists = dists.tolist()[0]
    neigh_ids = [ids["index2id"][i] for i in neigh_index[0]]

    if resource_id is not None and remove_duplicates:
        dists, neigh_ids = zip(*((d, oerid) for d, oerid in zip(dists, neigh_ids) if d > 1e-4 or oerid  == resource_id))

    if return_vectors or return_matrix or return_reduction or remove_duplicates:
        vectors = [resource_vector]
        gen = get_experimental_features(neigh_ids,
                                        [experiment_id],
                                        order_needed=False)
        dvect = {d["id"]: d["result"]["value"] for d in gen}
        for rid in neigh_ids:
            # To avoid the missing vectors in db but found in models files
            if rid in dvect:
                vectors.append(dvect[rid])
        # print("len vector", len(vectors))
    if return_matrix or return_reduction or remove_duplicates:
        matrix = pairwise_distances(vectors, metric="cosine")
    if remove_duplicates:
        matrix, vectors, dists, neigh_ids = filter_knn(matrix,
                                                       vectors,
                                                       dists,
                                                       neigh_ids)
    if return_reduction:
        reductor = dimension_reduction(reduction_type, len(vectors) - 1)
        matrix_projected = reductor.fit_transform(vectors)
    # print(len(neigh_ids))
    return {
            "top": None,
            "neighbors": neigh_ids,
            "distances": dists if return_dist else None,
            "vectors": vectors if return_vectors else None,
            "matrix": matrix.tolist() if return_matrix else None,
            "projected_matrix": matrix_projected.tolist() if return_reduction else None,
            "variance_ratio_": reductor.explained_variance_ratio_ if return_reduction and\
                                                                     (reduction_type=="PCA" or\
                                                                      reduction_type=="TruncatedSVD" or\
                                                                      reduction_type=="SparsePCA"
                                                                     )else None
            }


def knn_doc2vec_list(res_ids,
                     n_neighbors=20,
                     return_reduction=False,
                     return_vectors=False,
                     return_dist=False,
                     return_matrix=False,
                     reduction_type="PCA",
                     remove_duplicates=False,
                     resource_id=None):
    # assume not rendering resources with unfound knns: just keep the order
    nd_vectors = {d["id"]: d["result"]["value"] for d in get_experimental_features(res_ids, [experiment_id], order_needed=False)}
    res_ids, res_vectors = zip(*((x, nd_vectors.get(x, {})) for x in res_ids if x in nd_vectors))
    res_ids, res_vectors = list(res_ids), list(res_vectors)
    knnmodel = load_model('dcknlt')
    model = knnmodel[0]
    ids = knnmodel[1]
    dists, neigh_index = model.kneighbors(res_vectors, return_distance=True, n_neighbors=int(n_neighbors))
    dists = dists.tolist()
    neigh_ids = [[ids["index2id"][i] for i in neigix] for neigix in neigh_index]
    if return_vectors or return_matrix or return_reduction or remove_duplicates:
        vectors = []
        matrix = []
        matrix_projected = []
        for ix, vecrq in enumerate(neigh_ids):
            gen = get_experimental_features(vecrq,
                                            [experiment_id],
                                            order_needed=False)
            dvect = {d["id"]: d["result"]["value"] for d in gen}
            # To avoid the missing vectors in db but found in models files
            ngvects = [dvect.get(rid,()) for rid in vecrq if rid in dvect]
            vectors.append(ngvects)
            if return_matrix or return_reduction or remove_duplicates:
                ngmtx = pairwise_distances(ngvects, metric="cosine")
                matrix.append(ngmtx)
            if remove_duplicates:
                for j in dists[ix]:
                    matrix[ix], vectors[ix], dists[ix], neigh_ids[ix] = filter_knn(matrix[ix],
                                                                                   vectors[ix],
                                                                                   dists[ix],
                                                                                   neigh_ids[ix])
            if return_reduction:
                reductor = dimension_reduction(reduction_type, len(ngvects) - 1)
                ngmtx_pjtd = reductor.fit_transform(ngvects)
                matrix_projected.append(ngmtx_pjtd)
    return {
            "top": None,
            "neighbors": neigh_ids,
            "distances": dists if return_dist else None,
            "vectors": vectors if return_vectors else None,
            "matrix": matrix.tolist() if return_matrix else None,
            "projected_matrix": matrix_projected.tolist() if return_reduction else None,
            "variance_ratio_": reductor.explained_variance_ratio_ if return_reduction and\
                                                                     (reduction_type=="PCA" or\
                                                                      reduction_type=="TruncatedSVD" or\
                                                                      reduction_type=="SparsePCA"
                                                                     )else None
            }
