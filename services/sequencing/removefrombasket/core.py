from components.dataconnection.index import get_experimental_features
from x5gonwp3tools.tools.orderrecommendation.recommendsequence import remove_from_basket
from ..utils import distance_wikifiers
from SETTINGS import EXP_IDS

def get_resource_to_remove_from_basket(basket):
    # '''Return the id of a resource to remove from the basket'''
    nb_res = len(basket)
    # Download the wikifiers
    raw_wikifiers = list(get_experimental_features(basket, [EXP_IDS['wikifier']['SIMPLE']['experiment_id']]))
    wikifiers = {c['id']:c['result']['value']['concepts'] for c in raw_wikifiers}
    # Compute the distance
    computed_distances = {cid:{} for cid in basket}
    def distance(id1,id2):
        if id2 in computed_distances[id1]:
            return computed_distances[id1][id2]
        dist = distance_wikifiers(wikifiers[id1],wikifiers[id2])
        computed_distances[id1][id2] = dist
        computed_distances[id2][id1] = dist
        return dist
    return {"resource_id": remove_from_basket(basket,distance)}
