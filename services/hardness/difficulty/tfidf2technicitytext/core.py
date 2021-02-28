from x5gonwp3tools.tools.difficulty.difficulty import tfidf2technicity
from x5gonwp3models.modelloader import load_model
from x5gonwp3tools.tools.text2tfidf.tfidf import interpolates
from SETTINGS import EXP_IDS


# model = load_model('tfmllt[1-2]-grams')
experiment_id = EXP_IDS['text2tfidf']['[1-2]-grams']['experiment_id']


# Compute difficulty Vector from tfidf vectors of texts
def get_resource_difficulty(resource_texts):
    tfidfs = interpolates(resource_texts, load_model('tfmllt[1-2]-grams'), return_format="dict")
    return [{"resource_text": text,
             "value": tfidf2technicity(tfidf)} for text, tfidf in zip(resource_texts, tfidfs)]
