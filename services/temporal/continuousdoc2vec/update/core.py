from components.dataconnection.index import get_all_resource_ids, get_all_computed_resource_ids, insert_experiment_result, get_experimental_contents, get_experiment_results
from x5gonwp3tools.tools.continuousdoc2vec.continuousdoc2vec import train_a_part_model_fromdb, recover_vectors
import datetime
import tqdm
import joblib
import os
from sklearn.neighbors import NearestNeighbors
from x5gonwp3models.modelloader import load_model
from SETTINGS import EXP_IDS


id_tool = EXP_IDS['continuousdoc2vec']['V1']['tool_id']

__DEFAULT_RESUME_SETTING = False
__DEFAULT_EXPID_SETTING = EXP_IDS['continuousdoc2vec']['V1']['experiment_id']


def continuous_doc2vec_model_update_DB(resume: bool = __DEFAULT_RESUME_SETTING,
                                       exp_id: int = __DEFAULT_EXPID_SETTING):
    model = load_model('ccmllt')
    lids = list(get_all_resource_ids())
    if resume:
        lids_computed = list(get_all_computed_resource_ids(exp_id))
        print(f"We are talking about global nbr of resources: {len(lids)}")
        print(f"We are talking about nbr of computed resources: {len(lids_computed)}")
        lids = list(set(lids) - set(lids_computed))
        print(f"We are talking about nbr of tobe_computed resources: {len(lids)}")
    print("Some ids samples from DB that will be computed:")
    print(lids[0:100])
    # lids = lids[0:1002]
    chunk = 0
    records = {}
    batch_size = 1000
    for text, rid in ((t["content_raw"], t['id']) for t in tqdm.tqdm(get_experimental_contents(lids,
                                                                                               order_needed=False,
                                                                                               return_content_raw=True),
                                                                      total=len(lids),
                                                                      desc="continuousdoc2vec done")):
        try:
            if rid in model[0]:
                records[rid] = {'value': recover_vectors(rid, model),
                                'interpolate': False}
            else:
                records[rid] = {'value': recover_vectors(text, model),
                                'interpolate': True}
        except Exception as error:
            print("ErrorFATAL:", rid)
            print(error)
            records[rid] = {"value": {"error": str(error)}}
            raise error
        chunk += 1
        if chunk == batch_size:
            print("One part submitted to DB:")
            print(records.keys())
            insert_experiment_result(exp_id, records.items(), update=not resume)
            chunk = 0
            records = {}
    if chunk > 0 and chunk < batch_size:
        print("Last part submitted to DB:")
        print(records.keys())
        insert_experiment_result(exp_id, records.items(), update=not resume)


def continuous_doc2vec_createmodel():
    lids = list(get_all_resource_ids())
    print("Some ids samples from DB:")
    print(lids[0:100])
    batch_size = 1000
    ltexts = tqdm.tqdm(((res["id"],
                         res["content_raw"]) for res in get_experimental_contents(lids,
                                                                                  order_needed=True,
                                                                                  return_content_raw=True)),
                       total=len(lids),
                       desc="continuousdoc2vec_createmodel done")
    model = train_a_part_model_fromdb(ltexts,
                              f"x5gonwp3models/models/continuousdoc2vec/model/{datetime.date.today()}/{datetime.date.today()}",
                              vector_size=300,
                              window=5,
                              min_count=1)


def continuous_doc2vec_create_knn_model(exp_id: int = __DEFAULT_EXPID_SETTING):
    print("Some ids samples from DB:")
    rids, vectors = get_experiment_results(experiment_id=exp_id)
    part_vectors = []
    part_ids = []
    for rid, vect in zip(rids, vectors):
        part_ids.extend([f"{rid}p{j}" for j in range(len(vect))])
        part_vectors.extend(vect)
    print(len(part_ids))
    print("Vectors loaded")
    knn = NearestNeighbors(n_neighbors=20,
                           algorithm="auto",
                           metric="cosine",
                           n_jobs=-1).fit(part_vectors)

    outfolder = os.path.join("x5gonwp3models",
                             "models",
                             "continuousdoc2vec",
                             "knn",
                             str(datetime.date.today()))
    if not os.path.exists(outfolder):
        os.makedirs(outfolder)

    with open(os.path.join(outfolder,
                           f"{id_tool}_{exp_id}_knn_{str(datetime.date.today())}.pk"),
              "wb") as f:
        joblib.dump(knn, f)

    with open(os.path.join(outfolder,
                           f"{id_tool}_{exp_id}_knn_id_{str(datetime.date.today())}.pk"),
              "wb") as f:
        joblib.dump(dict(id2index=dict(zip(part_ids, list(range(len(part_ids))))), index2id=part_ids), f)
