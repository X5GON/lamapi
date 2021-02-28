from components.dataconnection.index import get_experimental_features
from SETTINGS import EXP_IDS


__DEFAULT_EXPID_SETTING = {
                  "CLASSIC": EXP_IDS['continuouswikifier']['CLASSIC']['experiment_id'],
                  "SIMPLE": EXP_IDS['continuouswikifier']['SIMPLE']['experiment_id'],
                  "FULL": EXP_IDS['continuouswikifier']['FULL']['experiment_id']
                 }

# Get continuousdoc2vec Vector from DB
def get_resource_continuouswikifier(resource_ids, wikification_type):
    recovered = get_experimental_features(resource_ids, [__DEFAULT_EXPID_SETTING[wikification_type]])
    return [{"resource_id": res["id"],
             "value": res["result"]["value"]} for res in recovered]
