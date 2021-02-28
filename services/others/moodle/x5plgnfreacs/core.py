from components.dataconnection.index import insert_grpa_ua
import json


# Build the mbz from the plalist
def store_mdl_group_data(access_infos):
    if type(access_infos['freacs']) == str:
        freacs = json.loads(access_infos['freacs'])
    else:
        freacs = access_infos['freacs']
    grpa_obj = {
                "tstamp":  access_infos['dt'],
                "acttype": freacs['acttype'],
                "crsuri": access_infos['rescrsurl'],
                "fre": freacs['fre'],
                "mdlmoduri": access_infos['resurl'],
                "actiondata": freacs,
                "crsdata": {"rescrstitle": access_infos['rescrstitle'],
                            "rescrsid": access_infos['rescrsid'],
                            "rescrsurl": access_infos['rescrsurl'],
                            "rescrssum": access_infos['rescrssum'],
                            "rescrslang": access_infos['rescrslang'],
                            "rescrsctg": access_infos['rescrsctg'],
                            "rescrsctgdesc": access_infos['rescrsctgdesc']},
                "mdlmoddata": {"title": access_infos['title'],
                               "description": access_infos['description'],
                               "author": access_infos['author'],
                               "language": access_infos['language'],
                               "creation_date": access_infos['creation_date'],
                               "type": access_infos['type'],
                               "mimetype": access_infos['mimetype'],
                               "license": access_infos['license'],
                               "licensename": access_infos['licensename'],
                               "resurl": access_infos['resurl'],
                               "resmdlid": access_infos['resmdlid'],
                               "residinhtml": access_infos['residinhtml'],
                               "resurlinpage": access_infos['resurlinpage']}
                }
    insert_grpa_ua([grpa_obj])
    return {"result": "success",
            "actions": "update",
            "pddata": ""}
