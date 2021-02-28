from components.dataconnection.index import get_experimental_contents


# Get Other Vector from DB
def get_resource_oermetainfos(resource_ids):
    recovered = get_experimental_contents(resource_ids)
    return [{"resource_id": res["id"],
             "value": res["value"]} for res in recovered]
