import os
from typing import Dict
import joblib
import datetime
import numpy as np
import tqdm
import operator
from scipy.sparse import dok_matrix
from sklearn.neighbors import NearestNeighbors
from components.dataconnection.index import (get_experimental_contents,
                                             get_all_resource_ids,
                                             get_experiment_results,
                                             insert_experiment_result)
from x5gonwp3tools.tools.text2tfidf.tfidf import tfidf_ngrams, save_model
from x5gonwp3tools.tools.text2processedtext.text2processedtext import preprocess
from SETTINGS import EXP_IDS


__DEFAULT_RESUME_SETTING = False
__DEFAULT_EXPID_SETTING = {
                "[1-2]-grams":  EXP_IDS['text2tfidf']['[1-2]-grams']['experiment_id'],
                "[1-1]-grams":  EXP_IDS['text2tfidf']['[1-1]-grams']['experiment_id'],
                "SIMPLE":  EXP_IDS['text2tfidf']['SIMPLE']['experiment_id'],
                }
# __DEFAULT_KNN_EXPID = 14
__DEFAULT_KNN_EXPID = EXP_IDS['text2tfidf']['[1-2]-grams']['experiment_id']
id_tool = EXP_IDS['text2tfidf']['SIMPLE']['tool_id']


def tfidf_model_update_DB(min_n: int = 1,
                          max_n: int = 2,
                          exp_id: Dict[str, int] = __DEFAULT_EXPID_SETTING,
                          batch_size: int = 1000
                          ):
    lids = list(get_all_resource_ids())
    print("Some ids samples from DB that will be computed:")
    print(lids[0:100])
    tfidf = {**{f"[{min_n}-{n}]-grams": {} for n in range(min_n, max_n + 1)},
             "SIMPLE": {}}
    records = {**{f"[{min_n}-{n}]-grams": {} for n in range(min_n, max_n + 1)},
               "SIMPLE": {}}
    chunk = 0
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # lids = lids[0:3]
    # print(lids)
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    for n in range(min_n, max_n + 1):

        path = os.path.join("x5gonwp3models",
                            "models",
                            "tfidf",
                            "model",
                            str(datetime.date.today()),
                            f"[{min_n}-{n}]-grams")
        ltexts, rlids = zip(*((preprocess(t["content_raw"]), t['id']) for t in tqdm.tqdm(get_experimental_contents(lids,
                                                                                                                   order_needed=False,
                                                                                                                   return_content_raw=True),
                                                                                 total=len(lids),
                                                                                 desc="tfidf done")))
        tfidf[f"[{min_n}-{n}]-grams"] = tfidf_ngrams(ltexts,
                                                     min_n=min_n,
                                                     max_n=n,
                                                     return_format="dict",
                                                     sort_keywords=(min_n == 1 and max_n ==2))
        save_model(path=path,
                   model=tfidf[f"[{min_n}-{n}]-grams"]["model"])
    for i, r in enumerate(rlids):
        try:
            for vname, res in tfidf.items():
                if vname == "SIMPLE":
                    continue
                records[vname][r] = {"value": tfidf[vname]['X'][i]}
                if vname == "[1-2]-grams":
                    sum_all_scores = sum(list(tfidf[vname]['X'][i].values()))
                    records["SIMPLE"][r] = {"value": dict(sorted(tfidf[vname]['X'][i].items(), key=operator.itemgetter(1))[-50:])}
                    records["SIMPLE"][r]["value_norm"] = {k: (v / sum_all_scores) for (k, v) in records["SIMPLE"][r]["value"].items()}
        except Exception as e:
            print(i, r)
            raise e
        chunk += 1
        if chunk == batch_size:
            # todo record in db
            insert_experiment_result(exp_id["[1-2]-grams"],
                                     records["[1-2]-grams"].items())
            insert_experiment_result(exp_id["[1-1]-grams"],
                                     records["[1-1]-grams"].items())
            insert_experiment_result(exp_id["SIMPLE"],
                                     records["SIMPLE"].items())
            records = {**{f"[{min_n}-{n}]-grams": {} for n in range(min_n, max_n + 1)},
                       "SIMPLE": {}}
            chunk = 0
    if chunk > 0 and chunk < batch_size:
        insert_experiment_result(exp_id["[1-2]-grams"],
                                 records["[1-2]-grams"].items())
        insert_experiment_result(exp_id["[1-1]-grams"],
                                 records["[1-1]-grams"].items())
        insert_experiment_result(exp_id["SIMPLE"],
                                 records["SIMPLE"].items())
        records = {**{f"[{min_n}-{n}]-grams": {} for n in range(min_n, max_n + 1)},
                   "SIMPLE": {}}
        chunk = 0


def tfidf_create_knn_model(id_experiment: int = __DEFAULT_KNN_EXPID):
    print("Vectors loading")
    rids, vectors = get_experiment_results(id_experiment,
                                           specific_fields=["value"])
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # rids = rids[0:15]
    # vectors = vectors[0:15]
    # print(rids)
    # print(vectors)
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    print("Create keywords index")
    index2keyword = list(set(sum(map(lambda x: list(x.keys()), vectors), [])))
    keyword2index = dict(zip(index2keyword, range(len(index2keyword))))
    print("Create sparse matrix")
    X = dok_matrix((len(rids), len(index2keyword)), dtype=np.float32)
    print(X.shape)
    for i, vector in tqdm.tqdm(enumerate(vectors),
                               total=len(vectors),
                               desc="sparsify vectors"):
        for k, v in vector.items():
            ind = keyword2index[k]
            X[i, ind] = v
    #
    knn = NearestNeighbors(n_neighbors=20,
                           algorithm="auto",
                           metric="cosine",
                           n_jobs=-1).fit(X)

    outfolder = os.path.join("x5gonwp3models",
                             "models",
                             "tfidf",
                             "knn",
                             str(datetime.date.today()))
    if not os.path.exists(outfolder):
        os.makedirs(outfolder)

    with open(os.path.join(outfolder,
                           f"{id_tool}_{id_experiment}_knn_{str(datetime.date.today())}_[1-2]-grams.pk"),
             "wb") as f:
        joblib.dump(knn, f)

    with open(os.path.join(outfolder,
                           f"{id_tool}_{id_experiment}_knn_id_{str(datetime.date.today())}_[1-2]-grams.pk"),
              "wb") as f:
        joblib.dump(dict(id2index=dict(zip(rids, list(range(len(rids))))),
                         index2id=rids),
                    f)

    with open(os.path.join(outfolder,
                           f"{id_tool}_{id_experiment}_knn_keyword_index_map_{str(datetime.date.today())}_[1-2]-grams.pk"),
              "wb") as f:
        joblib.dump(dict(index2keyword=index2keyword,
                         keyword2index=keyword2index),
                    f)
