from components.dataconnection.index import get_experimental_features
from x5gonwp3tools.tools.missingressources.missingressources import (
                                                    SelectorUnionInterstects,
                                                    predict_missing,
                                                    Selector
                                                    )
import tqdm
from SETTINGS import EXP_IDS


__DEFAULT_EXPID_SETTING = {
                  "CLASSIC": EXP_IDS['wikifier']['CLASSIC']['experiment_id'],
                  "SIMPLE": EXP_IDS['wikifier']['SIMPLE']['experiment_id'],
                  "FULL": EXP_IDS['wikifier']['FULL']['experiment_id']
                 }


# Previously : the "simple version was used exp_id=12": verify it!!!
def wikifier2candidates(names, wikifiers, score):
    data = {names[i]: {} for i in range(len(wikifiers))}
    for wik, name in tqdm.tqdm(zip(wikifiers, names),
                               total=len(wikifiers),
                               desc="Create wikifier candidates dict"):
        for c in wik['concepts']:
            data[name][c["title"]] = c[score]
    return data


def doc2vec2candidates(model, names, doc_ids):
    data = {}
    for doc_id, name in tqdm.tqdm(zip(doc_ids, names),
                                  total=len(names),
                                  desc="Create doc2vec candidates dict"):
        data[name] = dict(list(enumerate(model[doc_id].astype(float))))
    return data


def tfidf2candidates(X, features, names):
    # print(X.shape)
    data = {names[i]: {} for i in range(X.shape[0])}
    X.eliminate_zeros()
    rindex = X.nonzero()
    for r, c in tqdm.tqdm(zip(rindex[0], rindex[1]),
                          total=rindex[0].shape[0],
                          desc="Create tfidf candidates dict"):
        data[names[r]][features[c]] = X[r, c]
    return data


def predict_missing_deponcandidatetype(previous: int,
                                       after: int,
                                       candidate_ids: list,
                                       top_n_rate: float = 1/7,
                                       nb_processes: int = 1,
                                       selector: Selector = SelectorUnionInterstects,
                                       weighted: bool = True,
                                       candidatetype: str = 'wikifier',
                                       candidateexp: int = 4
                                       ):
    # Later: make it flexible: depending on candidatetype
    wiks = get_experimental_features([previous, after] + candidate_ids, [__DEFAULT_EXPID_SETTING["SIMPLE"]])
    ids, wiks = zip(*[(wik["id"], wik["result"]["value"]) for wik in wiks])

    wik_previous = wikifier2candidates([ids[0]], [wiks[0]], 'pageRank')
    wik_after = wikifier2candidates([ids[1]],[wiks[1]], 'pageRank')
    wik_candidates = wikifier2candidates(ids[2:], wiks[2:], 'pageRank')

    return predict_missing(previous=wik_previous.popitem(),
                           after=wik_after.popitem(),
                           candidates=wik_candidates,
                           top_n_rate=top_n_rate,
                           nb_processes=nb_processes,
                           selector=selector,
                           weighted=weighted
                           )
