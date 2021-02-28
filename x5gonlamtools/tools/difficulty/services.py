from components.dataconnection.index import *
from x5gonwp3tools.tools.difficulty.difficulty import tfidf2technicity


## Get tfidf Vector from DB
def get_tfidf2technicity(tfidf):
    return tfidf2technicity(tfidf['[1-2]-grams']['value'])
