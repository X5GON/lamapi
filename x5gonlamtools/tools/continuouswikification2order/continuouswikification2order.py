import itertools
from math import exp
from typing import List, Dict, Any, Text

ContinuousWikificationType = List[Dict[str,List[Dict[Text, Any]]]]

def average(l):
    """The average value of a list"""
    if len(l) == 0:
        return 0
    return sum(l)/len(l)


def sigmoid(x, slope=1):
    """The sigmoid function"""
    try:
        return 1/(1 + exp(-x*slope))
    except OverflowError:
        print("Overflow error on sigmoid")
        if x > 0:
            return 0
        else:
            return 1

def get_concepts_beginning_end(cwk):
    """Given a continuous wikifier, return two dictionnaries associating for \
       each concept the pageRanks at the beginning and at the end of the \
       resource"""
    nb_chunks = len(cwk)
    beginning = {}
    for i in range(nb_chunks//4):
        for concept in cwk[i]['concepts']:
            if concept['title'] in beginning:
                beginning[concept['title']].append(concept['pageRank'])
            else:
                beginning[concept['title']] = [concept['pageRank']]
    end = {}
    for i in range(nb_chunks-nb_chunks//4, nb_chunks):
        for concept in cwk[i]['concepts']:
            if concept['title'] in end:
                end[concept['title']].append(concept['pageRank'])
            else:
                end[concept['title']] = [concept['pageRank']]
    return beginning, end


def predecessor(beg1, end1, beg2, end2):
    """Predecessor function given the beginning and the end of two resources"""
    return ((average(beg2)*average(end1))-(average(end2)*average(beg1)))

def reordonize(cwk1, cwk2, slope=500):
    """Return a probability of the first resource to be before the second one (in terms of prerequisites)"""
    beg1, end1 = get_concepts_beginning_end(cwk1)
    beg2, end2 = get_concepts_beginning_end(cwk2)
    common_concepts = (set(beg1).intersection(set(end2))).union(set(beg2).intersection(set(end1)))
    c_scores = {c: predecessor(beg1.get(c, []),
                               end1.get(c, []),
                               beg2.get(c, []),
                               end2.get(c, [])) for c in common_concepts}
    sum_scores = sum(c_scores.values())
    pred = sigmoid(sum_scores, slope=slope)
    c_scores = {k: v/sum_scores  if sum_scores != 0 else 0 for k, v in c_scores.items()}
    return {'pred_score':pred, 'c_scores':c_scores}
