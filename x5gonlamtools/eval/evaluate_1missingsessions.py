import os
import csv
import json
import sys
import re
import tqdm
import numpy as np
from functools import partial
sys.path.append("../..")
from x5gonwp3tools.tools.missingressources.missingressources import predict_missing, SelectorSymDiffInterstects, SelectorUnionInterstects
from sklearn.metrics.pairwise import cosine_distances

EVALPATH = "/home/connes/code/yaleocw-corpus/data/MLCorpus/1MissingSessionCorpus/1MissingSessionCorpus.csv"
models = [entry.name for entry in os.scandir("./models")
                     if entry.name.endswith('.candidates.json')]

models = [
          "wikifier.cosine.candidates.json",
          "wikifier.pageRank.candidates.json",
          "processedtext.[1-2]-grams.tfidf.candidates.json",
          "processedtext.[1-3]-grams.tfidf.candidates.json",
          "phrased_3.[1-1]-grams.tfidf.candidates.json",
          "rawtext.doc2vec.candidates.json"
          ]

with open(EVALPATH, "r") as f:
    testset = [n for n in csv.reader(f, delimiter="|")]


def predict_cosine(previous, after, candidates):
    scores = {}
    for ncand, cand in candidates.items():
        scores[ncand] = (cosine_dist(cand, previous[1]) + cosine_dist(cand, after[1]))
    scores = list(sorted(scores.items(), key=lambda x: x[1]))
    return scores


def cosine_dist(candidate1, candidate2):
    commonkeys = list(set(candidate1.keys()) | set(candidate2.keys()))
    vec1 = np.array([candidate1.get(c, 0) for c in commonkeys]).reshape(1, -1)
    vec2 = np.array([candidate2.get(c, 0) for c in commonkeys]).reshape(1, -1)
    return cosine_distances(vec1, vec2)[0][0]


reg = re.compile(r"^(\d+)\-.*")
methods = [("our_union_w_1_baseline", partial(predict_missing,
                                              selector=SelectorUnionInterstects,
                                              weighted=True,
                                              top_n_rate=1.0,
                                              score_function="baseline")),
           ("our_union_w_1per7_baseline", partial(predict_missing,
                                                  selector=SelectorUnionInterstects,
                                                  weighted=True,
                                                  top_n_rate=1/7,
                                                  score_function="baseline")),
           ("our_sym_w_1_max", partial(predict_missing,
                                       selector=SelectorSymDiffInterstects,
                                       weighted=True,
                                       top_n_rate=1.0,
                                       score_function="max")),
           ("our_sym_w_1per7_max", partial(predict_missing,
                                           selector=SelectorSymDiffInterstects,
                                           weighted=True,
                                           top_n_rate=1/7,
                                           score_function="max")),
           ("our_union_w_1_max", partial(predict_missing,
                                         selector=SelectorUnionInterstects,
                                         weighted=True,
                                         top_n_rate=1.0,
                                         score_function="max")),
           ("our_union_w_1per7_max", partial(predict_missing,
                                             selector=SelectorUnionInterstects,
                                             weighted=True,
                                             top_n_rate=1/7,
                                             score_function="max")),
           ("our_sym_uw_1", partial(predict_missing,
                                    selector=SelectorSymDiffInterstects,
                                    weighted=False,
                                    top_n_rate=1.0)),
           ("our_union_uw_1per7", partial(predict_missing,
                                          selector=SelectorUnionInterstects,
                                          weighted=False,
                                          top_n_rate=1/7)),
           ("our_cos", predict_cosine)]
nb_s = len(testset) - 1


def eval_a_model(model):
    scores = {}
    print(f"Eval of {model}")
    with open(f"./models/{model}", "r") as f:
        candidates = json.load(f)

    # print(list(candidates.items())[0])
    names2ids, ids2names = {}, {}
    for k in candidates:
        idc = reg.match(k).groups()[0]
        names2ids[k] = str(idc)
        ids2names[str(idc)] = k
    for m, f in methods:
        scores[m] = {}
        good1, good10, fail, faillist = 0, 0, 0, []
        for SampleID, prevSid, afterSid, curSid in tqdm.tqdm(testset[1:],
                                                             desc=f"{model}_{m}"):
            try:
                prev = (ids2names[prevSid], candidates[ids2names[prevSid]])
                after = (ids2names[afterSid], candidates[ids2names[afterSid]])
                cur_name = ids2names[curSid]
                assert ids2names[curSid] in candidates
            except KeyError as e:
                fail += 1
                faillist.append((SampleID, prevSid, afterSid, curSid))
            scores[m][cur_name] = f(prev, after, candidates)
            top10 = list(filter(lambda x: x[0] not in [prev[0], after[0]],
                                scores[m][cur_name][0:12]))
            top10 = [x[0] for x in top10[0:10]]
            if cur_name in top10: good10 += 1
            if cur_name == top10[0]: good1 += 1
        nb_s = len(scores[m])
        print(f"{model}_{m} Top1: [{good1}/{nb_s}]~{good1/nb_s*100:.2f}")
        print(f"{model}_{m} Top10: [{good10}/{nb_s}]~{good10/nb_s*100:.2f}")
        print(f"{model}_{m} Failled: {fail}{faillist}")
    with open(f"./scores/{model}", "w") as f:
        json.dump(scores, f)
    print(f"Eval of {model} done")

# eval_a_model(models[0])

from joblib import Parallel, delayed
Parallel(n_jobs=len(models))(delayed(eval_a_model)(m) for m in models)

# _ = [eval_a_model(m) for m in models]
