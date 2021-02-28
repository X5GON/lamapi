from components.dataconnection.index import get_experimental_features
# from x5gonwp3tools.tools.continuouswikification2order.continuouswikification2order import reordonize
# from x5gonwp3tools.tools.RNN2order.continuousDoc2vec2order import reordonize
from x5gonwp3tools.tools.orderrecommendation.weighted_heuristic import generate_sequence_from_weighted_heuristic
from ..utils import distance_doc2vec
from ..utils import distance_wikifiers
from ..utils import reordonize
from SETTINGS import EXP_IDS
from x5gonwp3models.modelloader import load_model


def generate_adjacency_matrix(res_vectors, order_model="rnn2order"):
    adj_matrix = {one_id:{} for one_id in res_vectors}
    for id1,cwk1 in res_vectors.items():
        for id2,cwk2 in res_vectors.items():
            if id1 < id2:
                order = reordonize(order_model, cwk1, cwk2)["pred_score"]
                if order > 0.5: # We only consider the arc that have prerequisites
                    adj_matrix[id1][id2] = order
                else:
                    adj_matrix[id2][id1] = 1-order
    return adj_matrix

distance_to_compute = "wikifier" # 'wikifier' or 'doc2vec'


def get_sequence_and_distances(basket, order_model="rnn2order"):
    # '''Compute a sequence from the given basket, and also return the distances between each pair in the sequence.

    # We don't consider in the sequence two resources that are in the wrong order (in terms of prerequisites)'''
    # # Download the needed vectors for the suitable oredrmodeltype
    if order_model == "rnn2order":
        raw_res_vectors = list(get_experimental_features(basket, [EXP_IDS['continuousdoc2vec']['V1']['experiment_id']]))
    else:
        raw_res_vectors = list(get_experimental_features(basket, [EXP_IDS['continuouswikifier']['SIMPLE']['experiment_id']]))
    res_vectors = {c['id']:c['result']['value'] for c in raw_res_vectors}
    # Generate the adjacency matrix with the reordonize weights
    adj_matrix = generate_adjacency_matrix(res_vectors, order_model)
    # Apply the chosen algorithm to get a sequence
    sequence = generate_sequence_from_weighted_heuristic(adj_matrix)
    nb_res = len(sequence)
    # Compute the distance
    if distance_to_compute == "wikifier":
        res_wikifier = list(get_experimental_features(basket, [EXP_IDS['wikifier']['SIMPLE']['experiment_id']]))
        res_wikifier = {c['id']:c['result']['value']['concepts'] for c in res_wikifier}
        intra_distances = [distance_wikifiers(res_wikifier[sequence[i]],res_wikifier[sequence[i+1]]) for i in range(nb_res-1)]
    elif distance_to_compute == "doc2vec":
        res_d2v = list(get_experimental_features(basket, [EXP_IDS['doc2vec']['V1']['experiment_id']]))
        res_d2v = {c['id']:c['result']['value'] for c in res_d2v}
        intra_distances = [distance_doc2vec(res_d2v[sequence[i]],res_d2v[sequence[i+1]]) for i in range(nb_res-1)]
    else:
        raise ValueError("the distance you inputted is not allowed")
    return {"sequence": sequence,
            "distances": intra_distances}
