from components.dataconnection.index import get_experimental_features
from SETTINGS import EXP_IDS


experiment_id = EXP_IDS['doc2vec']['V1']['experiment_id']


# Get doc2vec Vector from DB
def get_resource_doc2vec(resource_ids):
    recovered = get_experimental_features(resource_ids, [experiment_id])
    return [{"resource_id": res["id"],
             "value": res["result"]["value"]} for res in recovered]
