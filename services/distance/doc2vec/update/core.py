import datetime
import os
import joblib
import tqdm
from sklearn.neighbors import NearestNeighbors
from components.dataconnection.index import (get_experimental_contents,
                                             get_all_computed_resource_ids,
                                             get_all_resource_ids,
                                             get_experiment_results,
                                             insert_experiment_result)
from x5gonwp3tools.tools.doc2vec.doc2vec import (load_model, recover_vector,
                                                 train_a_model_fromdb)
from x5gonwp3models.modelloader import load_model
from SETTINGS import EXP_IDS


id_tool = EXP_IDS['doc2vec']['V1']['tool_id']
experiment_id = EXP_IDS['doc2vec']['V1']['experiment_id']

__DEFAULT_RESUME_SETTING = False
__DEFAULT_EXPID_SETTING = EXP_IDS['doc2vec']['V1']['experiment_id']


def doc2vec_model_update_DB(resume: bool = __DEFAULT_RESUME_SETTING,
                            exp_id: int = __DEFAULT_EXPID_SETTING
                           ):
    model = load_model('dcmllt')
    lids = list(get_all_resource_ids())
    if resume:
        lids_computed = list(get_all_computed_resource_ids(exp_id))
        print("We are talking about global nbr of resources: ", len(lids))
        print("We are talking about nbr of computed resources: ", len(lids_computed))
        lids = list(set(lids) - set(lids_computed))
        print("We are talking about nbr of tobe_computed resources: ", len(lids))
    print("Some ids samples from DB that will be computed:")
    print(lids[100:])
    # lids = lids[-100:]
    chunk = 0
    records = {}
    batch_size = 1000
    for r, t in tqdm.tqdm(((res["id"],
                            res["content_raw"]) for res in get_experimental_contents(lids,
                                                                                     order_needed=False,
                                                                                     return_content_raw=True)),
                          total=len(lids),
                          desc="doc2vec done"):
        try:
            try:
                records[r] = {'value': recover_vector(r, model).tolist(),
                              'interpolate': False}
            except KeyError:
                records[r] = {'value': recover_vector(t, model).tolist(),
                              'interpolate': True}
        except Exception as e:
            print("ErrorFATAL:", r)
            print(e)
            records[r] = {'value': {"error": str(e)}}
            # raise e
        chunk += 1
        if chunk == batch_size:
            # todo record in db
            print("One part submitted to DB:")
            print(records.keys())
            insert_experiment_result(exp_id, records.items(), update=not resume)
            chunk = 0
            records = {}
    if chunk > 0 and chunk < batch_size:
        print("Last part submitted to DB:")
        print(records.keys())
        insert_experiment_result(exp_id, records.items(), update=not resume)


def doc2vec_createmodel():
    lids = list(get_all_resource_ids())
    print("Some ids samples from DB:")
    print(lids[0:100])
    batch_size = 1000
    ltexts = tqdm.tqdm(((res["id"],
                         res["content_raw"]) for res in get_experimental_contents(lids,
                                                                                  return_content_raw=True)),
                        total=len(lids),
                        desc="doc2vec_createmodel done")
    train_a_model_fromdb(ltexts, "x5gonwp3models/models/doc2vec/model/"+str(datetime.date.today())+"/"+str(datetime.date.today()),
                         vector_size=300,
                         window=5,
                         min_count=1)


def doc2vec_create_knn_model(exp_id: int = __DEFAULT_EXPID_SETTING):
    print("Some ids samples from DB:")
    rids, vectors = get_experiment_results(experiment_id=experiment_id)
    print(vectors[:2])
    print(len(rids), len(vectors), len(vectors[0]))
    print("Vectors loaded")
    knn = NearestNeighbors(n_neighbors=20,
                           algorithm="auto",
                           metric="cosine",
                           n_jobs=-1).fit(vectors)

    outfolder = os.path.join("x5gonwp3models",
                             "models",
                             "doc2vec",
                             "knn",
                             str(datetime.date.today()))
    if not os.path.exists(outfolder):
        os.makedirs(outfolder)

    with open(os.path.join(outfolder,
                           f"{id_tool}_{experiment_id}_knn_{str(datetime.date.today())}.pk"),
              "wb") as f:
        joblib.dump(knn, f)

    with open(os.path.join(outfolder,
                           f"{id_tool}_{experiment_id}_knn_id_{str(datetime.date.today())}.pk"),
              "wb") as f:
        joblib.dump(dict(id2index=dict(zip(rids, list(range(len(rids))))), index2id=rids), f)
