import datetime
import operator
import os
import joblib
import numpy as np
import tqdm
from scipy.sparse import dok_matrix
from sklearn.neighbors import NearestNeighbors

from components.dataconnection.index import (get_all_computed_resource_ids,
                                             get_all_resource_ids,
                                             get_experiment_results,
                                             get_experimental_contents,
                                             insert_experiment_result)
from x5gonwp3tools.tools.wikifier.wikification import (wikification,
                                                       wikification_filter)
from SETTINGS import EXP_IDS

id_tool = EXP_IDS['wikifier']['SIMPLE']['tool_id']
__DEFAULT_RESUME_SETTING = False
__DEFAULT_EXPID_SETTING = {
                  "CLASSIC": EXP_IDS['wikifier']['CLASSIC']['experiment_id'],
                  "SIMPLE": EXP_IDS['wikifier']['SIMPLE']['experiment_id'],
                  "FULL": EXP_IDS['wikifier']['FULL']['experiment_id']
                 }
# __DEFAULT_KNN_EXPID = 13
__DEFAULT_KNN_EXPID = __DEFAULT_EXPID_SETTING["CLASSIC"]


def wikifier_model_update_DB(resume: bool = __DEFAULT_RESUME_SETTING,
                             exp_id: dict = __DEFAULT_EXPID_SETTING,
                             batch_size: int = 1000
                             ):
    lids = list(get_all_resource_ids())
    if resume:
        lids_computed = list(get_all_computed_resource_ids(exp_id["CLASSIC"]))
        print("We are talking about global nbr of resources: ", len(lids))
        print("We are talking about nbr of computed resources: ",
              len(lids_computed))
        lids = list(set(lids) - set(lids_computed))
        print("We are talking about nbr of tobe_computed resources: ",
              len(lids))
    print("Some ids samples from DB that will be computed:")
    print(lids[0:100])
    wikifier = {"FULL": {}, "CLASSIC": {}, "SIMPLE": {}}
    records = {"FULL": {}, "CLASSIC": {}, "SIMPLE": {}}
    chunk = 0
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # lids = lids[:3]
    # print(lids)
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    for r, t in tqdm.tqdm(((res["id"],
                            res["content_raw"]) for res in get_experimental_contents(lids,
                                                                                     order_needed=False,
                                                                                     return_content_raw=True)),
                          total=len(lids),
                          desc="wikifier done"):
        try:
            wikifier_full_tmp = wikification(t,
                                             subprocess=4,
                                             wikification_type="FULL")
            wikifier["FULL"][r] = wikifier_full_tmp
            wikifier["CLASSIC"][r] = wikification_filter(wikifier_full_tmp,
                                                         wikification_type_needed="CLASSIC")
            wikifier["SIMPLE"][r] = wikification_filter(wikifier["CLASSIC"][r],
                                                        wikification_type_needed="SIMPLE")
        except Exception as e:
            print("ErrorFATAL:", r)
            wikifier["FULL"][r] = {"error": str(e)}
            wikifier["CLASSIC"][r] = {"error": str(e)}
            wikifier["SIMPLE"][r] = {"error": str(e)}
            # print(e)
        records["FULL"][r] = {'value': wikifier["FULL"][r]}
        records["CLASSIC"][r] = {'value': wikifier["CLASSIC"][r]}
        records["SIMPLE"][r] = {'value': wikifier["SIMPLE"][r]}
        chunk += 1
        if chunk == batch_size:
            # todo record in db
            print("One part submitted to DB:")
            insert_experiment_result(exp_id["FULL"],
                                     records["FULL"].items(), update=not resume)
            insert_experiment_result(exp_id["CLASSIC"],
                                     records["CLASSIC"].items(), update=not resume)
            insert_experiment_result(exp_id["SIMPLE"],
                                     records["SIMPLE"].items(), update=not resume)
            wikifier = {"FULL": {}, "CLASSIC": {}, "SIMPLE": {}}
            records = {"FULL": {}, "CLASSIC": {}, "SIMPLE": {}}
            chunk = 0
    if chunk > 0 and chunk <= batch_size:
        print("Last part submitted to DB:")
        insert_experiment_result(exp_id["FULL"],
                                 records["FULL"].items(), update=not resume)
        insert_experiment_result(exp_id["CLASSIC"],
                                 records["CLASSIC"].items(), update=not resume)
        insert_experiment_result(exp_id["SIMPLE"],
                                 records["SIMPLE"].items(), update=not resume)
        wikifier = {"FULL": {}, "CLASSIC": {}, "SIMPLE": {}}
        records = {"FULL": {}, "CLASSIC": {}, "SIMPLE": {}}
        chunk = 0


def wikifier_create_knn_model(id_experiment: int = __DEFAULT_KNN_EXPID,
                              score=lambda c: c["pageRank"]):
    print("Vectors loading")
    rids, vectors = get_experiment_results(id_experiment,
                                           specific_fields=["value",
                                                            "concepts"])
    print("Create concepts index")
    index2concept = list(set(map(operator.itemgetter("url"),
                                 sum(vectors, [])
                                 )))
    concept2index = dict(zip(index2concept, range(len(index2concept))))
    print("Create sparse matrix")
    X = dok_matrix((len(vectors), len(index2concept)), dtype=np.float32)
    print(X.shape)
    for i, vector in tqdm.tqdm(enumerate(vectors),
                               total=len(vectors),
                               desc="sparsify vectors"):
        for c in vector:
            ind = concept2index[c["url"]]
            X[i, ind] = score(c)

    knn = NearestNeighbors(n_neighbors=20,
                           algorithm="auto",
                           metric="cosine",
                           n_jobs=-1).fit(X)

    outfolder = os.path.join("x5gonwp3models",
                             "models",
                             "wikifier",
                             "knn",
                             str(datetime.date.today()))
    if not os.path.exists(outfolder):
        os.makedirs(outfolder)

    with open(os.path.join(outfolder,
                           f"{id_tool}_{id_experiment}_knn_{str(datetime.date.today())}.pk"),
             "wb") as f:
        joblib.dump(knn, f)

    with open(os.path.join(outfolder,
                           f"{id_tool}_{id_experiment}_knn_id_{str(datetime.date.today())}.pk"),
              "wb") as f:
        joblib.dump(dict(id2index=dict(zip(rids, list(range(len(rids))))),
                         index2id=rids),
                    f)

    with open(os.path.join(outfolder,
                           f"{id_tool}_{id_experiment}_knn_concept_index_map_{str(datetime.date.today())}.pk"),
              "wb") as f:
        joblib.dump(dict(index2concept=index2concept,
                         concept2index=concept2index),
                    f)
