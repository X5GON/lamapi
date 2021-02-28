from components.dataconnection.index import get_experimental_features
from components.dataconnection.index import get_resource_description
from x5gonwp3models.modelloader import load_model
from x5gonwp3tools.tools.difficulty.difficulty import __wpm, wikification2con_per_sec, tfidf2technicity
# from x5gonwp3tools.tools.continuouswikification2order.continuouswikification2order import reordonize as rzecw2order
# from x5gonwp3tools.tools.RNN2order.continuousDoc2vec2order import reordonize as rzernn2order
from x5gonwp3tools.tools.orderrecommendation.recommendsequence import recommend_between_sequence, is_considered_distance
import sklearn.metrics.pairwise as skdist
import numpy as np
from scipy.sparse import dok_matrix
from SETTINGS import EXP_IDS
from ..utils import distance_wikifiers, wikifier_to_vector
from ..utils import reordonize


def get_knn_one_resource(resource_wikifier, n_neighbors, forbidden_ids=[]):
    """Given a resource wikifier (list of concepts), return the ids of the nearest neighbors"""
    model, concept_map, ids = load_model('wrknlt')
    resource_vector = dok_matrix((1, len(concept_map["index2concept"])),
                                 dtype=np.float32)
    not_found = 0
    for concept in resource_wikifier:
        try:
            ind = concept_map["concept2index"][concept["url"]]
            resource_vector[0, ind] = concept["pageRank"]
        except KeyError:
            not_found += 1
    dists, _neigh_index = model.kneighbors(resource_vector,
                                           n_neighbors=n_neighbors,
                                           return_distance=True)
    dists = dists.tolist()[0]
    neigh_ids = [ids["index2id"][i] for i in _neigh_index[0]]
    dists, neigh_ids = zip(*((d, oerid) for d, oerid in zip(dists, neigh_ids) if d > 1e-4 and oerid not in forbidden_ids))
    return neigh_ids


def get_knn_resources(resource_wikifiers, n_neighbors):
    """Given a dict mapping resource ids to wikifiers, return a dict mapping resource ids to their nearest neighbors"""
    return {current_id: get_knn_one_resource(current_wikifier, n_neighbors, forbidden_ids=set(resource_wikifiers)) for current_id, current_wikifier in resource_wikifiers.items()}


def generate_possible_of_two_balls(ball1, ball2, forbidden_ids, index_to_database_id):
    ball1 = {index_to_database_id[index]:distance for distance,index in zip(*ball1)}
    ball1 = {index_to_database_id[index]:distance for distance,index in zip(*ball2)}
    intersection = {}
    for index in ball1:
        if index in ball2 and index not in forbidden_ids:
            intersection[index] = (ball1[index],ball2[index])
    return intersection


def generate_possible(sequence, resource_wikifiers):
    dist_to_next = [distance_wikifiers(resource_wikifiers[sequence[i]], resource_wikifiers[sequence[i+1]]) for i in range(len(sequence)-1)]
    dist_balls = [dist_to_next[i] if i == 0 else (max(dist_to_next[i],dist_to_next[i-1]) if i < len(sequence)-1 else dist_to_next[i-1]) for i in range(len(sequence))]
    vectors = {c_id:wikifier_to_vector(wk) for c_id,wk in resource_wikifiers.items()}
    model, concept_map, ids = load_model('wrknlt')
    balls = [model.radius_neighbors([vectors[sequence[i]]], dist_balls[i]) for i in range(len(sequence))]
    return [generate_possible_of_two_balls(balls[i],balls[i+1], sequence, ids["index2id"]) for i in range(len(sequence)-1)]


def format_resources(insertions, max_concepts):
    added_ids = [c for c in insertions if c != None]
    if added_ids == []:
        return insertions
    resources_needed_infos = get_resource_description(added_ids,
                                                      {"concepts": EXP_IDS['wikifier']['SIMPLE']['experiment_id'],
                                                       "keywords": EXP_IDS['text2tfidf']['SIMPLE']['experiment_id']},
                                                      max_concepts=max_concepts)

    resources_final_infos = {}
    for rid in added_ids:
        res_infos = resources_needed_infos.get(int(rid), dict())
        if res_infos:
            res_infos['duration'] = 60 * (res_infos['len_word'] / __wpm()["Slide"])
            res_infos['difficulty'] = wikification2con_per_sec(res_infos['len_char'], res_infos['len_concepts'])
            # res_infos['difficulty'] = tfidf2technicity( res_infos['keywords_full'] )
            del res_infos['keywords_full']
            del res_infos['wikifier_full']
        resources_final_infos[rid] = res_infos
    return [None if v == None else {'resource':resources_final_infos[v], 'confidence': 0.5} for v in insertions]


def get_resources_to_insert(sequence, max_concepts, order_model="rnn2order"):
    # '''Compute a sequence from the given basket, and also return the distances between each pair in the sequence.
    # We don't consider in the sequence two resources that are in the wrong order (in terms of prerequisites)'''

    # Download the knn of the input resources, and get the continuous wikifiers and wikifier representations
    wikifiers = list(get_experimental_features(sequence, [EXP_IDS['wikifier']['SIMPLE']['experiment_id']]))
    wikifiers_data = {c['id']:c['result']['value']['concepts'] for c in wikifiers}
    ids_to_knn = get_knn_resources(wikifiers_data, 100)
    new_knn_ids = list({knn_id for knn in ids_to_knn.values() for knn_id in knn})
    new_knn_wikifiers = list(get_experimental_features(new_knn_ids, [EXP_IDS['wikifier']['SIMPLE']['experiment_id']]))
    for wik in new_knn_wikifiers:
        wikifiers_data[wik['id']] = wik['result']['value']['concepts']
    ids_to_knn = {cid:[knn for knn in knns if knn in wikifiers_data] for cid,knns in ids_to_knn.items()}
    # memoized functions that compute the distance for two resources
    all_ids = list(wikifiers_data)
    distances_memo = {one_id:{} for one_id in all_ids}
    def distance_fun(id1,id2):
        if id2 in distances_memo[id1]:
            return distances_memo[id1][id2]
        distance = distance_wikifiers(wikifiers_data[id1], wikifiers_data[id2])
        distances_memo[id1][id2] = distance
        distances_memo[id2][id1] = distance
        return distance
    possible_with_distances = [[nei for nei in ids_to_knn[sequence[i]]+ids_to_knn[sequence[i+1]] if is_considered_distance(sequence[i],sequence[i+1],nei,distance_fun)] for i in range(len(sequence)-1)]
    all_ids = list(set([nei for neighbors in possible_with_distances for nei in neighbors]+sequence))

    if order_model == "rnn2order":
        res_vectors = list(get_experimental_features(all_ids, [EXP_IDS['continuousdoc2vec']['V1']['experiment_id']]))
    else:
        res_vectors = list(get_experimental_features(all_ids, [EXP_IDS['continuouswikifier']['SIMPLE']['experiment_id']]))
    res_vectors_data = {c['id']:c['result']['value'] for c in res_vectors}
    order_memo = {one_id:{} for one_id in all_ids}
    def order(id1,id2):
        if id2 in order_memo[id1]:
            return order_memo[id1][id2]
        order = reordonize(order_model, res_vectors_data[id1], res_vectors_data[id2])['pred_score']
        order_memo[id1][id2] = order
        order_memo[id2][id1] = 1-order
        return order
    return {"sequence": sequence,
            "insertions": format_resources(recommend_between_sequence(sequence, possible_with_distances, distance_fun, order), max_concepts)}
