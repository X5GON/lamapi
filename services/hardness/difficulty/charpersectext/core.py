from x5gonwp3tools.tools.difficulty.difficulty import char_per_sec


# Compute difficulty Vector from texts
def get_resource_difficulty(resource_texts):
    return [{"resource_text": res,
             "value": char_per_sec(length=len(res))} for res in resource_texts]
