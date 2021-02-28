#!/usr/bin/env python
# coding: utf-8
from types import SimpleNamespace
from sklearn.linear_model import LinearRegression, DecisionTreeRegressor
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
import pickle
#


def __build_apparition(cws, context_size, scorer):
    for i, cw in enumerate(cws):
        apparition = {}
        for slice, w in enumerate(cw):
            words = w["words"]
            for rank, c in w["concepts"]:
                if c["url"] not in apparition:
                    apparition[c["url"]] = []
                for sup in c["support"]:
                    mini = min(0, sup["wFrom"] - context_size)
                    maxi = max(len(words), sup["wTo"] + context_size)
                    suptext = words[mini:maxi]
                    apparition[c["url"]].append({"suptext": suptext,
                                                 "ires": i,
                                                 "islid": slice,
                                                 "score": scorer(c)})
        yield apparition


def __create_dataset(cws, context_size, fnovelty, scorer):
    dataset = []
    appgen = __build_apparition(cws, context_size, scorer)
    for cw in cws:
        sample = next(appgen)
        for curl, track in sample.items():
            novelgen = fnovelty(track)
            for sample in enumerate(track):
                dataset.append((track["suptext"],
                                next(novelgen),
                                track["ires"],
                                track["islid"]))
    return np.array(dataset)


def novelty(track):
    hscore = np.array()
    hdist = np.array()
    cur_slice = 0
    for sample in track:
        if cur_slice != sample["islid"]:
            cur_slice = sample["islid"]
            hdist += np.ones_like(hdist.shape)
        yield sample["score"] - (hscore * hdist.T).sum()
        hscore = np.append(hscore, [sample["score"]])
        hdist = np.append(hdist, [1])


def __train(dataset, model):
    pass


def __test(dataset, model):
    pass


# def vocabulary2order():
#     pass
#
# def predict_serie(model, samplelist):
#     pass
#
#
# def __score_of_samples():
#     pass
#
# def predict_from_cwkep(model, ep1, ep2):
#     samples_ep1 = __cwkserie2samplelist([ep1])
#     samples_ep2 = __cwkserie2samplelist([ep2])
#     samples2score(model, samples_ep1)
#     samples2score(model, samples_ep2)
#
#
#
#
# def __concept2sample(concept, words, context_size):
#     cname = concept["title"]
#     curl = concept["url"]
#     cPR = concept["pageRank"]
#     ccos = concept["cosine"]
#     for sup in concept["support"]:
#         sample = SimpleNamespace()
#         bounds = slice(max(0, sup['wFrom'] - context_size),
#                        min(sup['wTo'] + context_size + 1, len(words)))
#         sample.text = words[sup['wFrom']:sup['wTo'] + 1]
#         sample.concept = cname
#         sample.url = curl
#         sample.PR = cPR
#         sample.cos = ccos
#         sample.context = words[bounds]
#         sample.centroid = np.mean([sup['wFrom'], sup['wTo'] + 1]) - bounds.start
#     return sample
#
#
# def __cwkserie2samplelist(cwklist, context_size):
#     for sid, serie in enumerate(cwklist):
#         for epid, episode in enumerate(serie):
#             for slid, wk in enumerate(episode):
#                 for concept in wk["annotations"]:
#                     sample = __concept2sample(concept,
#                                               wk["words"], context_size)
#                     sample.sid = sid
#                     sample.epid = epid
#                     sample.slid = slid
#                     yield sample
#
#
# def __wkserie2samplelist(wklist, context_size):
#     for sid, serie in enumerate(wklist):
#         for epid, wk in enumerate(serie):
#             for concept in wk["annotations"]:
#                 sample = __concept2sample(concept,
#                                           wk["words"], context_size)
#                 sample.sid = sid
#                 sample.epid = epid
#                 yield sample
#
#
# def __compute_ser_novelties(serie_samples, novelty_score):
#     ep = []
#     nolvelty_cum = 0
#     for sample in serie_samples:
#         if ep and sample.epid == ep[-1].epid:
#             sample.novelty = 1 - nolvelty_cum
#             if novelty_score == "PR":
#                 nolvelty_cum += sample.PR
#             if novelty_score == "cos":
#                 nolvelty_cum += sample.cos
#             ep.append(sample)
#         else:
#             if ep:
#                 yield ep
#             sample.novelty = 1
#             nolvelty_cum = 0
#             ep = [sample]
#     yield ep
#
#
# def __compute_ep_novelties(serie_samples, novelty_score):
#     sl = []
#     nolvelty_cum = 0
#     for sample in serie_samples:
#         if sl and sample.slid == sl[-1].slid:
#             sample.novelty = 1 - nolvelty_cum
#             if novelty_score == "PR":
#                 nolvelty_cum += sample.PR
#             if novelty_score == "cos":
#                 nolvelty_cum += sample.cos
#             sl.append(sample)
#         else:
#             if sl:
#                 yield sl
#             sample.novelty = 1
#             nolvelty_cum = 0
#             sl = [sample]
#     yield sl
#
#
# def __cwkseries2novelties(cwklist, context_size, novelty_scope, novelty_score):
#     gen1 = __cwkserie2samplelist(cwklist, context_size)
#     if novelty_scope == "serie":
#         return __compute_ser_novelties(gen1, novelty_score)
#     else:
#         assert(novelty_scope == "episod")
#         return __compute_ep_novelties(gen1, novelty_score)
#
#
# def __wkseries2novelties(wklist, context_size, novelty_score):
#     return __compute_ser_novelties(__wkserie2samplelist(wklist, context_size),
#                                    novelty_score)
#
#
# def __train_novelty_model(samplelist, model_outpath,
#                           model, vectorizer_outpath):
#     # DecisionTreeRegressor(max_depth=15)
#     # LinearRegression()
#     vectorizer = CountVectorizer()
#     y_train = []
#     bag_of_word = []
#     for n in samplelist:
#         y_train.append(n.novelty)
#         bag_of_word.append(" ".join(n.context))
#     bag_of_word = vectorizer.fit_transform(bag_of_word).toarray()
#     if vectorizer_outpath:
#         with open(vectorizer_outpath, "wb") as f:
#             pickle.dump(vectorizer, f)
#     model.fit(bag_of_word, y_train)
#     if model_outpath:
#         with open(model_outpath, "wb") as f:
#             pickle.dump(model, f)
#     return model
