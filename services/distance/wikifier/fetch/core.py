from components.dataconnection.index import get_experimental_features
from x5gonwp3tools.tools.wikifier.wikification import wikification
from SETTINGS import EXP_IDS


__DEFAULT_WIKIFIER_EXPIDS_SETTING = {
                 "CLASSIC": EXP_IDS['wikifier']['CLASSIC']['experiment_id'],
                 "SIMPLE": EXP_IDS['wikifier']['SIMPLE']['experiment_id'],
                 "FULL": EXP_IDS['wikifier']['FULL']['experiment_id']
                 }


# Get wikifier Vector from DB
def get_resource_wikifier(resource_ids, wikification_type):
    # print(resource_ids)
    recovered = get_experimental_features(resource_ids, [__DEFAULT_WIKIFIER_EXPIDS_SETTING[wikification_type]])
    return [{"resource_id": res["id"],
             "value": res["result"]["value"]} for res in recovered]


# Get wikifier
def get_wikifier(resource_texts, wikification_type):
    # print(resource_ids)
    return [{"text": text,
             "value": wikification(text=text,
                                   wikification_type=wikification_type)
                                   } for text in resource_texts]
