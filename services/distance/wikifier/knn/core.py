from components.dataconnection.index import get_experimental_features
from scipy.sparse import dok_matrix, vstack
from sklearn.metrics import pairwise_distances


import numpy as np
from x5gonwp3models.modelloader import load_model
from x5gonwp3tools.tools.wikifier.wikification import wikification
from SETTINGS import EXP_IDS
from utils import dimension_reduction, filter_knn, time_usage


# Get knn_wikifier model from the global SETTINGS: 'wrknlt'=latestWikifierKnnModel
# knnmodel = load_model('wrknlt')
experiment_id = EXP_IDS['wikifier']['SIMPLE']['experiment_id']


def knn_wikifier_res(resource_id, **kwargs):
    wik = next(get_experimental_features([resource_id],
                                         [experiment_id]))["result"]["value"]
    res = __knn_wikifier(resource_wikifier=wik,
                         resource_id=resource_id,
                         **kwargs)
    res.update(resource_id=resource_id)
    return res


def knn_wikifier_vect(vector, **kwargs):
    res = __knn_wikifier(resource_wikifier=vector, **kwargs)
    return res


def knn_wikifier_text(resource_text, **kwargs):
    wik = wikification(resource_text, wikification_type="SIMPLE")
    return __knn_wikifier(resource_wikifier=wik, **kwargs)


@time_usage
def __knn_wikifier(resource_wikifier,
                   score=lambda c: c["pageRank"],
                   n_neighbors=20,
                   return_reduction=False,
                   return_vectors=False,
                   return_dist=False,
                   return_matrix=False,
                   reduction_type="TruncatedSVD",
                   remove_duplicates=False,
                   resource_id=None):
    concept_map=load_model('wrknlt')[1]
    model=load_model('wrknlt')[0]
    ids=load_model('wrknlt')[2]
    top = None
    resource_wikifier = resource_wikifier["concepts"]
    resource_vector = dok_matrix((1, len(concept_map["index2concept"])),
                                 dtype=np.float32)
    not_found = 0
    for r in resource_wikifier:
        try:
            ind = concept_map["concept2index"][r["url"]]
            resource_vector[0, ind] = score(r)
        except KeyError:
            not_found += 1
    dists, _neigh_index = model.kneighbors(resource_vector,
                                           n_neighbors=n_neighbors,
                                           return_distance=True)
    dists = dists.tolist()[0]
    neigh_ids = [ids["index2id"][i] for i in _neigh_index[0]]

    if resource_id is not None and remove_duplicates:
        dists, neigh_ids = zip(*((d, oerid) for d, oerid in zip(dists, neigh_ids) if d > 1e-4 or oerid  == resource_id))

    if return_vectors or return_matrix or return_reduction or remove_duplicates:
        gen = get_experimental_features(neigh_ids, [experiment_id],
                                        order_needed=False)
        neighbors_wikifier = {d["id"]: d["result"]["value"]["concepts"] for d in gen}
        neighbors_vector = dok_matrix((len(neighbors_wikifier), len(concept_map["index2concept"])),
                                      dtype=np.float32)
        for i, rid in enumerate(neigh_ids):
            if rid in neighbors_wikifier:
                for c in neighbors_wikifier[rid]:
                    ind = concept_map["concept2index"][c["url"]]
                    neighbors_vector[i, ind] = score(c)
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
        top = []
        for i in range(reductor.components_.shape[0]):
            top_ = sorted(enumerate(reductor.components_[i].tolist()), key=lambda x: x[1], reverse=True)
            top_ = map(lambda x: (concept_map["index2concept"][x[0]], x[1]), top_)
            top_ = list(filter(lambda x: x[1] != 0, top_))
            top.append(top_)
    if return_vectors:
        json_vectors = [{} for _ in range(vectors.shape[0])]
        for k, v in vectors.todok().items():
            json_vectors[k[0]][concept_map["index2concept"][k[1]]] = float(v)
    return {  # "resource_id": resource_id,
            "resource_wikifier": resource_wikifier,
            "neighbors": neigh_ids,
            "concept_not_found": not_found,
            "distances": dists if return_dist else None,
            "vectors": json_vectors if return_vectors else None,
            "matrix": matrix.tolist() if return_matrix else None,
            "projected_matrix": matrix_projected.tolist() if return_reduction else None,
            "top": top,
            "variance_ratio_": reductor.explained_variance_ratio_ if return_reduction and\
                                                                     (reduction_type=="PCA" or\
                                                                      reduction_type=="TruncatedSVD" or\
                                                                      reduction_type=="SparsePCA"
                                                                     )else None
            }


@time_usage
def knn_wikifier_list(res_ids,
                      score=lambda c: c["pageRank"],
                      n_neighbors=20,
                      return_reduction=False,
                      return_vectors=False,
                      return_dist=False,
                      return_matrix=False,
                      reduction_type="TruncatedSVD",
                      remove_duplicates=False,
                      resource_id=None):
    concept_map = load_model('wrknlt')[1]
    model = load_model('wrknlt')[0]
    ids = load_model('wrknlt')[2]
    top = None
    # Here the order/missingOnes won't be a problem: because we be used unordred + issued from a knn(forcely is in DB)
    # But better keep the order even if there is missing ones
    res_gen = get_experimental_features(res_ids, [experiment_id])
    res_wiks = {x['id']: x['result']['value']['concepts'] for x in res_gen}
    res_ids, res_wikifiers = zip(*((x, res_wiks.get(x, {})) for x in res_ids if x in res_wiks))
    res_ids, res_wikifiers = list(res_ids), list(res_wikifiers)
    res_vectors = dok_matrix((len(res_wikifiers), len(concept_map["index2concept"])),
                             dtype=np.float32)
    not_found = []
    for rix, rwk in enumerate(res_wikifiers):
        nt_fd = 0
        for r in rwk:
            try:
                ind = concept_map["concept2index"][r["url"]]
                res_vectors[rix, ind] = score(r)
            except KeyError:
                nt_fd += 1
        not_found.append(nt_fd)
    dists, _neigh_index = model.kneighbors(res_vectors,
                                           n_neighbors=int(n_neighbors),
                                           return_distance=True)
    dists = dists.tolist()
    neigh_ids = [[ids["index2id"][i] for i in neigix] for neigix in _neigh_index]

    # if resource_id is not None and remove_duplicates:
    #     dists, neigh_ids = zip(*((d, oerid) for d, oerid in zip(dists, neigh_ids) if d > 1e-4 or oerid  == resource_id))

    if return_vectors or return_matrix or return_reduction or remove_duplicates:
        vectors = []
        matrix = []
        matrix_projected = []
        top = []
        for ix, vecrq in enumerate(neigh_ids):
            gen = get_experimental_features(vecrq, [experiment_id],
                                            order_needed=False)
            neighbors_wikifier = {d["id"]: d["result"]["value"]["concepts"] for d in gen}
            neighbors_vector = dok_matrix((len(neighbors_wikifier), len(concept_map["index2concept"])),
                                          dtype=np.float32)
            for i, rid in enumerate(vecrq):
                for c in neighbors_wikifier[rid]:
                    ind = concept_map["concept2index"][c["url"]]
                    neighbors_vector[i, ind] = score(c)
            ngvects = vstack((res_vectors, neighbors_vector))
            vectors.append(ngvects)
            # print(type(ngvects))
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
                reductors = []
                reductor = dimension_reduction(reduction_type, ngvects.shape[0] - 1)
                ngmtx_pjtd = reductor.fit_transform(ngvects)
                matrix_projected.append(ngmtx_pjtd)
                ngtop = []
                for i in range(reductor.components_.shape[0]):
                    top_ = sorted(enumerate(reductor.components_[i].tolist()), key=lambda x: x[1], reverse=True)
                    top_ = map(lambda x: (concept_map["index2concept"][x[0]], x[1]), top_)
                    top_ = list(filter(lambda x: x[1] != 0, top_))
                    ngtop.append(top_)
                top.append(ngtop)
                reductors.append(reductor)
            if return_vectors:
                json_vectors = []
                json_vectors.append([{} for _ in range(ngvects.shape[0])])
                for k, v in ngvects.todok().items():
                    json_vectors[ix][k[0]][concept_map["index2concept"][k[1]]] = float(v)
    return {  # "resource_id": resource_id,
            "resource_wikifier": res_wikifiers,
            "neighbors": neigh_ids,
            "concept_not_found": not_found,
            "distances": dists if return_dist else None,
            "vectors": json_vectors if return_vectors else None,
            "matrix": matrix.tolist() if return_matrix else None,
            "projected_matrix": matrix_projected.tolist() if return_reduction else None,
            "top": top,
            "variance_ratio_": [rd.explained_variance_ratio_ for rd in reductors] if return_reduction and\
                                                                                (reduction_type=="PCA" or\
                                                                                 reduction_type=="TruncatedSVD" or\
                                                                                 reduction_type=="SparsePCA"
                                                                                )else None
            }
