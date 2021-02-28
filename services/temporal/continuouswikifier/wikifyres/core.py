from components.dataconnection.index import get_experimental_contents
from x5gonwp3tools.tools.continuouswikifier.continuouswikifier import continuous_wikification


# Get continuouswikifier Vector from DB
def compute_resource_continuouswikifier(*, resource_ids, **kwargs):
    recovered = get_experimental_contents(resource_ids,
                                          return_content_raw=True)
    return [{"resource_id": res["id"],
             "value": continuous_wikification(res["content_raw"], **kwargs)} for res in recovered]
