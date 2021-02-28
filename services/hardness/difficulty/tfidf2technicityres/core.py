from x5gonwp3tools.tools.difficulty.difficulty import tfidf2technicity
from components.dataconnection.index import get_experimental_features
from SETTINGS import EXP_IDS


__DEFAULT_EXPID_SETTING = {
                "[1-2]-grams":  EXP_IDS['text2tfidf']['[1-2]-grams']['experiment_id'],
                "[1-1]-grams":  EXP_IDS['text2tfidf']['[1-1]-grams']['experiment_id'],
                "SIMPLE":  EXP_IDS['text2tfidf']['SIMPLE']['experiment_id'],
                }


# Get difficulty Vector from tfidf vectors in DB
def get_resource_difficulty(resource_ids):
    recovered = get_experimental_features(resource_ids, [__DEFAULT_EXPID_SETTING["[1-2]-grams"]])
    return [{"resource_id": res["id"],
             "value": tfidf2technicity(res["result"]['value'])} for res in recovered]
