from components.dataconnection.index import *
from x5gonwp3tools.tools.continuouswikifier.continuouswikifier import continuous_wikification, continuouswikification_filter
import tqdm
from SETTINGS import EXP_IDS


# id_tool = 6
id_tool = EXP_IDS['continuouswikifier']['SIMPLE']['tool_id']
__DEFAULT_RESUME_SETTING = False
__DEFAULT_EXPID_SETTING = {
                  "CLASSIC": EXP_IDS['continuouswikifier']['CLASSIC']['experiment_id'],
                  "SIMPLE": EXP_IDS['continuouswikifier']['SIMPLE']['experiment_id'],
                  "FULL": EXP_IDS['continuouswikifier']['FULL']['experiment_id']
                 }
__DEFAULT_KNN_EXPID = __DEFAULT_EXPID_SETTING['SIMPLE']


def continuouswikifier_model_update_DB(resume: bool = __DEFAULT_RESUME_SETTING,
                                       exp_id: dict = __DEFAULT_EXPID_SETTING,
                                       batch_size: int = 100
                                       ):
    lids = list(get_all_resource_ids())
    if resume:
        lids_computed = list(get_all_computed_resource_ids(exp_id["CLASSIC"]))
        print("We are talking about global nbr of resources: ", len(lids))
        print("We are talking about nbr of computed resources: ", len(lids_computed))
        lids = list(set(lids) - set(lids_computed))
        print("We are talking about nbr of tobe_computed resources: ", len(lids))
    print("Some ids samples from DB that will be computed:")
    print(lids[0:100])
    continuouswikifier = {}
    continuouswikifier = {"FULL": {}, "CLASSIC": {}, "SIMPLE": {}}
    records = {"FULL": {}, "CLASSIC": {}, "SIMPLE": {}}
    chunk = 0
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # lids = lids[:3]
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    for r, t in tqdm.tqdm(((res["id"],
                            res["content_raw"]) for res in get_experimental_contents(lids,
                                                                                     order_needed=True,
                                                                                     return_content_raw=True)),
                          total=len(lids),
                          desc="continuouswikifier done"):
        try:
            continuouswikifier_full_tmp = continuous_wikification(t,
                                                                  subprocess=[5,1],
                                                                  wikification_type="FULL"
                                                                  )
            continuouswikifier["FULL"][r] = continuouswikifier_full_tmp
            continuouswikifier["CLASSIC"][r] = continuouswikification_filter(continuouswikifier_full_tmp,
                                                                             wikification_type_needed="CLASSIC")
            continuouswikifier["SIMPLE"][r] = continuouswikification_filter(continuouswikifier["CLASSIC"][r],
                                                                            wikification_type_needed="SIMPLE")
        except Exception as e:
            print("ErrorFATAL:", r)
            continuouswikifier["FULL"][r] = {"error": str(e)}
            continuouswikifier["CLASSIC"][r] = {"error": str(e)}
            continuouswikifier["SIMPLE"][r] = {"error": str(e)}
        records["FULL"][r] = {'value': continuouswikifier["FULL"][r]}
        records["CLASSIC"][r] = {'value': continuouswikifier["CLASSIC"][r]}
        records["SIMPLE"][r] = {'value': continuouswikifier["SIMPLE"][r]}
        chunk += 1
        if chunk == batch_size:
            try:
                # todo record in db
                print("One part submitted to DB:")
                insert_experiment_result(exp_id["FULL"],
                                         records["FULL"].items(), update=not resume)
                insert_experiment_result(exp_id["CLASSIC"],
                                         records["CLASSIC"].items(), update=not resume)
                insert_experiment_result(exp_id["SIMPLE"],
                                         records["SIMPLE"].items(), update=not resume)
            except Exception as er:
                print("Insert error:", er)
                print("Non inserted IDs:", records["FULL"].keys())
                # raise er
            continuouswikifier = {"FULL": {}, "CLASSIC": {}, "SIMPLE": {}}
            records = {"FULL": {}, "CLASSIC": {}, "SIMPLE": {}}
            chunk = 0
    if chunk > 0 and chunk < batch_size:
        try:
            print("Last part submitted to DB:")
            insert_experiment_result(exp_id["FULL"],
                                     records["FULL"].items(), update=not resume)
            insert_experiment_result(exp_id["CLASSIC"],
                                     records["CLASSIC"].items(), update=not resume)
            insert_experiment_result(exp_id["SIMPLE"],
                                     records["SIMPLE"].items(), update=not resume)
        except Exception as er:
            print("Insert error:", er)
            print("Non inserted IDs:", records["FULL"].keys())
        continuouswikifier = {"FULL": {}, "CLASSIC": {}, "SIMPLE": {}}
        records = {"FULL": {}, "CLASSIC": {}, "SIMPLE": {}}
        chunk = 0
    continuouswikifier = {"FULL": {}, "CLASSIC": {}, "SIMPLE": {}}
    records = {"FULL": {}, "CLASSIC": {}, "SIMPLE": {}}
