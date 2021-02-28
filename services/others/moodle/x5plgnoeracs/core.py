from components.dataconnection.index import (get_grpa_oeracsdata)
# from SETTINGS import EXP_IDS


# OERs access data
def get_mdlplgnoeracs_data(freobj_infos):
    oeracsdata = get_grpa_oeracsdata(freobj_infos,
                                     spec_res=freobj_infos['oers'],
                                     spec_fres=['x5recommend', 'x5discovery', 'x5playlist'])
    oersacsfdata = [oeracsdata.get(ac, {"oerid": ac,
                                        "nbacess": 0,
                                        "tspacess": ""})
                    for i, ac in enumerate(freobj_infos['oers'])]
    return {"result": "success",
            "rltdetails": "",
            "actions": "update ui",
            "pddata": oersacsfdata}
