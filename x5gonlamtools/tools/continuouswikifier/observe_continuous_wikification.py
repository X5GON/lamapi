#!/usr/bin/env python
# coding: utf-8

# In[1]:


import plotly.graph_objs as go
# import plotly.figure_factory as ff
# from IPython.display import display, clear_output, HTML
from plotly.offline import iplot, plot
# , init_notebook_mode

import os
import itertools
# import pprint
import pickle
import re
import numpy as np
import pandas as pd
# from functools import partial
# from ipywidgets import widgets
from operator import itemgetter
# from argparse import Namespace
# init_notebook_mode()
CORPUS_PATH = "../../../predict-series/res/YaleSeriesCorpus/"


# In[2]:


def recover_episodes(serie_path):
    textpaths = []
    episodes = []
    cwpaths = []
    for root, dirs, files in os.walk(serie_path):
        for file in files:
            if file == "continuous_wikification_settings(bunch_size=5000,window_seek=100,overlap=2500))":
                cwpaths.append(os.path.join(root, file))
            if file == "rawtext":
                textpaths.append(os.path.join(root, file))
                episodes.append(os.path.split(root)[1])
    episodes, textpaths, cwpaths = zip(*sorted(zip(episodes, textpaths, cwpaths),
                                               key=lambda x: int(re.match(r"(\d+).*", x[0]).group(1))))
    
    return [(episode, dict(textpath=textpath, cwpath=cwpath))
                            for episode, textpath, cwpath in zip(episodes, textpaths, cwpaths)]


# In[3]:


def recover_lecture_concepts(episodes, ep1, ep2):
    # load 
    with open(episodes[ep1]['cwpath'], "rb") as f: cw1 = pickle.load(f)
    with open(episodes[ep2]['cwpath'], "rb") as f: cw2 = pickle.load(f)
    ep1name, ep2name = ep1, ep2
    cdict, distri, es, epnumber = {}, [], len(cw1), 0
    
    for part in itertools.chain(cw1, cw2):
        for c in part:
            t = c["title"]
            try:
                cdict[t]["x"] += [epnumber]
                cdict[t]["y"] += [c["pageRank"]]
            except KeyError: cdict[t] = dict(x=[epnumber], y=[c["pageRank"]])
        epnumber += 1

    epbounds = [dict(bounds=(0, es), title=ep1name),
                dict(bounds=(es, epnumber), title=ep2name)]
    ss, es = epbounds[0]["bounds"]
    se, ee = epbounds[1]["bounds"]
    columns = ["title", "x", "y", "limit", "common"]
    
    for c, d in cdict.items():
        accept = set(d["x"]).intersection(np.arange(ss, es)) and set(d["x"]).intersection(np.arange(se, ee))
        x, y = zip(*sorted(zip(d["x"], d["y"]), key=itemgetter(0)))
       
        limit = len(x) if x[-1] < es else next(i for i, val in enumerate(x) if val >= es)
        
        data = [c, x, y, limit, bool(accept)]
            
        distri.append({k: v for k, v in zip(columns, data)})

    distri = sorted(distri, key=lambda d: len(d['x']), reverse=True)
    df = pd.DataFrame(distri, columns=columns)

    return df, epbounds


# ## Series loading

# In[4]:


series = sorted([(d.name, d.path) for d in os.scandir(CORPUS_PATH)],
                key=itemgetter(0))[:-2]
seriesnames, seriespath = zip(*series)

nb_samples = 0
nb_good = 0
missed = []
epmeans = []
# epstds = []
# epcstds = []

def __weighted_avg_std(values, weights):
    average = np.average(values, weights=weights)
    # Fast and numerically precise:
    variance = np.average((values - average)**2, weights=weights)
    return average, np.sqrt(variance)
    
for sid, serpath in enumerate(seriespath[:-2]):
    print(f"Serie:[{sid}/{len(seriespath[:-2])}]")
    epnames, eppaths = zip(*sorted(recover_episodes(serpath),
                                    key=lambda x: int(re.match(r"(\d+).*", x[0]).group(1))))
    for epi in range(1, len(eppaths)):
        # print(f"Couple:[{epi}/{len(eppaths)}]")
        dfconcepts, epbounds = recover_lecture_concepts({name: paths for name, paths in zip(epnames, eppaths)},
                                                        epnames[epi - 1],
                                                        epnames[epi])
        ss, es = epbounds[0]["bounds"]
        se, ee = epbounds[1]["bounds"]
        dfcs = dfconcepts[dfconcepts["common"]]
        nb_samples += 1
        ep1mean, ep2mean = [], []
        # ep1std, ep2std = [], [] 
        for ci, df in enumerate(dfcs.itertuples()):
            # print(f"Concept:[{ci}/{dfcs.shape[0]}]")
            ep1m, ep1s = __weighted_avg_std(np.array(df.x[:df.limit])/(es - ss - 1),
                                            df.y[:df.limit])
            
            ep2m, ep2s = __weighted_avg_std((np.array(df.x[df.limit:]) - se)/(ee - se - 1),
                                            df.y[df.limit:])
            ep1mean.append(ep1m)
            # ep1std.append(ep1std)
            ep2mean.append(ep2m)
            # ep2std.append(ep2std)
        
        sep1, sep2 = np.mean(ep1mean), np.mean(ep2mean)
        if sep1 > sep2: nb_good += 1
        else: missed.append((seriesnames[sid], epnames[epi - 1], epnames[epi]))

        epmeans.append((sep1, sep2))
        # epstds.append((np.mean(ep1std), np.mean(ep2std)))
        # epcstds.append((np.std(ep1mean), np.std(ep2mean)))

print(f"[{nb_good}/{nb_samples}] good predictions")


# In[ ]:


x1, x2 = zip(*epmeans)
# std1, std2 = zip(*epstds)
# cstd1, cstd2 = zip(*epcstds)
print("Mean slice:", np.mean(x1), np.mean(x2))
# print("Standard deviation of slice:", np.mean(std1), np.mean(std2))
# print("Standard deviation of concept:", np.mean(cstd1), np.mean(cstd2))
print("Standard deviation of mean apparition across episodes:", np.std(x1), np.std(x2))
trace1 = dict(x=x1, name="Ep previous", type="box")
trace2 = dict(x=x2, name="Ep after", type="box")
data=[trace1, trace2]
layout= go.Layout(title="Mean slides for previous and after episodes", xaxis=dict(title="Mean sildes"))
fig = go.Figure(data, layout)
plot(fig)






