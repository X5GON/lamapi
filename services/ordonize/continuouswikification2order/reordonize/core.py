from components.dataconnection.index import get_experimental_features
from x5gonwp3tools.tools.continuouswikification2order.continuouswikification2order import reordonize
from SETTINGS import EXP_IDS


__DEFAULT_EXPID_SETTING = {
                  "CLASSIC": EXP_IDS['continuouswikifier']['CLASSIC']['experiment_id'],
                  "SIMPLE": EXP_IDS['continuouswikifier']['SIMPLE']['experiment_id'],
                  "FULL": EXP_IDS['continuouswikifier']['FULL']['experiment_id']
                 }


# Previuously used exp_id=6 : must verify !!
def get_resource_continuouswikification2order(resource_id, candidate_ids):
    cands_cwk = get_experimental_features(candidate_ids, [__DEFAULT_EXPID_SETTING["SIMPLE"]])
    res_cwk = get_experimental_features([resource_id], [__DEFAULT_EXPID_SETTING["SIMPLE"]])
    res_cwk = [s['result']['value'] for s in res_cwk]
    res_cwk = res_cwk[0]
    try:
        res = {}
        for c in cands_cwk:
            res[c['id']] = reordonize(res_cwk, c['result']['value'])
        return res
    except ValueError:
        return ""
    return {"resource_id": resource_id,
            "value": res}
