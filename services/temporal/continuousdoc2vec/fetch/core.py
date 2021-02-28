from components.dataconnection.index import get_experimental_features
from SETTINGS import EXP_IDS


__DEFAULT_EXPID_SETTING = EXP_IDS['continuousdoc2vec']['V1']['experiment_id']


# Get continuousdoc2vec Vector from DB
def get_resource_continuousdoc2vec(resource_ids):
    recovered = get_experimental_features(resource_ids, [__DEFAULT_EXPID_SETTING])
    return [{"resource_id": res["id"],
             "value": res["result"]["value"]} for res in recovered]
