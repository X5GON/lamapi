from x5gonwp3tools.tools.difficulty.difficulty import wikification2con_per_sec
from components.dataconnection.index import get_experimental_contents, get_experimental_features
from SETTINGS import EXP_IDS


__DEFAULT_EXPID_SETTING = {
                  "CLASSIC": EXP_IDS['wikifier']['CLASSIC']['experiment_id'],
                  "SIMPLE": EXP_IDS['wikifier']['SIMPLE']['experiment_id'],
                  "FULL": EXP_IDS['wikifier']['FULL']['experiment_id']
                 }


# Get difficulty Vector from DB
# Previously : the "simple version was used exp_id=12": verify it!!!
def get_resource_difficulty(resource_ids):
    res_lens = get_experimental_contents(resource_ids)
    res_wks = get_experimental_features(resource_ids, [__DEFAULT_EXPID_SETTING["SIMPLE"]])
    res_valid = get_valid_resources(res_lens, res_wks)
    return [{"resource_id": res[0],
             "value": wikification2con_per_sec(res[1], len(res[2]['concepts']))} for res in res_valid]


def get_valid_resources(res_lens, res_wks):
    list_res_lens = list(res_lens)
    list_res_wks = list(res_wks)
    for l in list_res_lens:
        for wk in list_res_wks:
            if wk['id'] == l['id'] and l['language'] == 'en':
                yield l['id'], l["value"], wk["result"]["value"]
