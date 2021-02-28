from components.dataconnection.index import get_experimental_features
from SETTINGS import EXP_IDS


__DEFAULT_EXPID_SETTING = {
                "[1-2]-grams":  EXP_IDS['text2tfidf']['[1-2]-grams']['experiment_id'],
                "[1-1]-grams":  EXP_IDS['text2tfidf']['[1-1]-grams']['experiment_id'],
                "SIMPLE":  EXP_IDS['text2tfidf']['SIMPLE']['experiment_id'],
                }


# Get tfidf Vector from DB
def get_resource_tfidf(resource_ids, tfidf_type):
    recovered = get_experimental_features(resource_ids, [__DEFAULT_EXPID_SETTING[tfidf_type]])
    return [{"resource_id": res["id"],
             "value": res["result"]} for res in recovered]
