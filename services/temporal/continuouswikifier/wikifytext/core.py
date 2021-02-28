from x5gonwp3tools.tools.continuouswikifier.continuouswikifier import continuous_wikification


# Get continuouswikifier Vector from Texts
def compute_resource_continuouswikifier(*, resource_texts, **kwargs):
    return [{"resource_text": res,
             "value": continuous_wikification(res)} for res in resource_texts]
