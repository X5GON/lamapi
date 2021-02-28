from x5gonwp3tools.tools.difficulty.difficulty import char_per_sec
from components.dataconnection.index import get_experimental_contents


# Get difficulty Vector from DB
def get_resource_difficulty(resource_ids):
    recovered = get_experimental_contents(resource_ids)
    return [{"resource_id": res["id"],
             "value": char_per_sec(res["value"])} for res in recovered]
