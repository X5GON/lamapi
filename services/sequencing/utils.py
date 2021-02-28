import sklearn.metrics.pairwise as skdist
from x5gonwp3models.modelloader import load_model
from x5gonwp3tools.tools.continuouswikification2order.continuouswikification2order import reordonize as rzecw2order
from x5gonwp3tools.tools.RNN2order.continuousDoc2vec2order import reordonize as rzernn2order
from scipy.sparse import dok_matrix
import numpy as np


def wikifier_to_vector(resource_wikifier):
    """Given a list of concepts with pageRanks, return a vector representing the wikifier"""
    concept_map=load_model('wrknlt')[1]
    model=load_model('wrknlt')[0]
    ids=load_model('wrknlt')[2]
    top = None
    resource_vector = dok_matrix((1, len(concept_map["index2concept"])),
                                 dtype=np.float32)
    not_found = 0
    for r in resource_wikifier:
        try:
            ind = concept_map["concept2index"][r["url"]]
            resource_vector[0, ind] = r['pageRank']
        except KeyError:
            not_found += 1
    return resource_vector


def distance_doc2vec(d2v1, d2v2):
    """Compute the distance distance between two doc2vec.
    It is not a metric because two different objects can have distance 0 (colinear vectors)"""
    return skdist.pairwise_distances(X=[d2v1,d2v2], metric="cosine", n_jobs=-1)[0,1]


def distance_wikifiers(wk1, wk2):
    """Compute the distance between two wikifiers.
    It is not a metric because two different objects can have distance 0 (colinear vectors)"""
    index_to_url = list({concept['url'] for concept in wk1+wk2})
    url_to_index = {index_to_url[i]:i for i in range(len(index_to_url))}
    v1 = [0]*len(index_to_url)
    for concept in wk1:
        v1[url_to_index[concept['url']]] = concept['pageRank']
    v2 = [0]*len(index_to_url)
    for concept in wk2:
        v2[url_to_index[concept['url']]] = concept['pageRank']
    res = skdist.pairwise_distances(X=[v1,v2], metric="cosine", n_jobs=1)[0,1]
    return res


def reordonize(modeltype, vec1, vec2):
    if modeltype == "cw2order":
        # based on cwikifier vectors
        return rzecw2order(vec1, vec2)
    elif modeltype == "rnn2order":
        rnn2ordermodel = load_model('rrmllt')
        # based on cdoc2vec vectors
        return rzernn2order(rnn2ordermodel, vec1, vec2)
