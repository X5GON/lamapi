from x5gonwp3tools.tools.difficulty.difficulty import wikification2con_per_sec
from x5gonwp3tools.tools.wikifier.wikification import wikification


# Compute difficulty Vector from texts
def get_resource_difficulty(resource_texts):
    return [{"resource_text": res,
             "value": wikification2con_per_sec(len(res), len(wikification(res, wikification_type='SIMPLE')['concepts']))} for res in resource_texts]
