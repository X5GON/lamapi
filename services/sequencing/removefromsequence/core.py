from components.dataconnection.index import get_experimental_features
from x5gonwp3tools.tools.orderrecommendation.recommendsequence import remove_between_sequence
from ..utils import distance_wikifiers
from SETTINGS import EXP_IDS

def get_resource_to_remove_from_sequence(sequence):
    # '''Return the id of a resource to remove from the sequence (while keeping the other resources in the same order)'''
    nb_res = len(sequence)
    # Download the wikifiers
    raw_wikifiers = list(get_experimental_features(sequence, [EXP_IDS['wikifier']['SIMPLE']['experiment_id']]))
    wikifiers = {c['id']:c['result']['value']['concepts'] for c in raw_wikifiers}
    # Compute the distance
    computed_distances = {cid:{} for cid in sequence}
    def distance(id1,id2):
        if id2 in computed_distances[id1]:
            return computed_distances[id1][id2]
        dist = distance_wikifiers(wikifiers[id1],wikifiers[id2])
        computed_distances[id1][id2] = dist
        computed_distances[id2][id1] = dist
        return dist
    return {"resource_id": remove_between_sequence(sequence,distance)}
