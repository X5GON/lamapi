import datetime
import os
import re
import joblib

from x5gonwp3tools.tools.continuousdoc2vec.continuousdoc2vec import load_model as continuousdoc2vecLoader
from x5gonwp3tools.tools.doc2vec.doc2vec import load_model as doc2vecLoader
from x5gonwp3tools.tools.text2tfidf.tfidf import load_model as tfidfLoader
from x5gonwp3tools.tools.RNN2order.continuousDoc2vec2order import load_model as c2v2orderLoader
import sys
# sys.path.insert(0, "./x5gonwp3tools/tools/UserData")
# from x5gonwp3tools.tools.UserData.src.Generation.GenerationGraph import GenerationGraph


def _local_models(root):
    __local_models = {}
    path = os.path.normpath(root)
    path = path.split(os.sep)
    init_depth = len(path)
    for dirpath, dirnames, filenames in os.walk(root):
        path = os.path.normpath(dirpath)
        path = path.split(os.sep)
        depth = len(path) - init_depth
        if depth == 0:
            __local_models = {mname: {} for mname in dirnames}
        elif depth == 1:
            mname = path[-1]
            __local_models[mname] = {tname: {} for tname in dirnames}
        elif depth == 2:
            mname = path[-2]
            tname = path[-1]
            __local_models[mname][tname] = {date: [] for date in dirnames}
        elif depth == 3:
            mname = path[-3]
            tname = path[-2]
            date = path[-1]
            __local_models[mname][tname][date] = filenames
    # print(__local_models)
    return __local_models, root

# Models loading configs
AUTO_LOAD = {"dcknlt": ("doc2vec", "knn", "latest", None),
             "dcmllt": ("doc2vec", "model", "latest", None),
             "wrknlt": ("wikifier", "knn", "latest", None),
             "tfknlt[1-2]-grams": ("tfidf", "knn", "latest", "[1-2]-grams"),
             "tfmllt[1-2]-grams": ("tfidf", "model", "latest", "[1-2]-grams"),
             "ccmllt": ("continuousdoc2vec", "model", "latest", None),
             "rrmllt": ("RNNordonator", "model", "latest", None),
             # "teanlt2r": ("text2phrase", "all_text_transciption", "latest", "2gramsphraser"),
             # "teanlt3r": ("text2phrase", "all_text_transciption", "latest", "3gramsphraser"),
             # "teanlt4r": ("text2phrase", "all_text_transciption", "latest", "4gramsphraser"),
             # "teanlt5r": ("text2phrase", "all_text_transciption", "latest", "5gramsphraser"),
             #####"teaalt2r": ("text2phrase", "all_wikipedia", "latest", "2gramsphraser"),
             #####"teaalt3r": ("text2phrase", "all_wikipedia", "latest", "3gramsphraser"),
             # "teaalt4r": ("text2phrase", "all_wikipedia", "latest", "4gramsphraser"),
             # "teaalt5r": ("text2phrase", "all_wikipedia", "latest", "5gramsphraser"),
             #####"teanlt2r": ("text2phrase", "all_x5gon", "latest", "2gramsphraser"),
             #####"teanlt3r": ("text2phrase", "all_x5gon", "latest", "3gramsphraser"),
             # "teanlt4r": ("text2phrase", "all_x5gon", "latest", "4gramsphraser"),
             # "teanlt5r": ("text2phrase", "all_x5gon", "latest", "5gramsphraser")
             }

LOCAL_MODELS, ROOT = _local_models(root="x5gonwp3models/models/")

LOADED_MODELS = {}

_KNN_DOC_REGEX = [re.compile(r"\d+\_\d+\_knn\_\d+\-\d+\-\d+_?(.*)\.pk"),
                  re.compile(r"\d+\_\d+\_knn\_id\_\d+\-\d+\-\d+\_?(.*)\.pk")]

_KNN_WIK_REGEX = [re.compile(r"\d+_\d+\_knn\_\d+\-\d+\-\d+\_?(.*)\.pk"),
                  re.compile(r"\d+_\d+\_knn\_concept\_index\_map\_\d+\-\d+\-\d+\_?(.*)\.pk"),
                  re.compile(r"\d+_\d+\_knn\_id_\d+\-\d+\-\d+\_?(.*)\.pk")]

_KNN_TFIDF_REGEX = [re.compile(r"\d+_\d+\_knn\_\d+\-\d+\-\d+\_?(.*)\.pk"),
                    re.compile(r"\d+_\d+\_knn\_keyword\_index\_map\_\d+\-\d+\-\d+\_?(.*)\.pk"),
                    re.compile(r"\d+_\d+\_knn\_id_\d+\-\d+\-\d+\_?(.*)\.pk")]


def load_model(ident, tool=None, mtype=None, date="latest", extra=None, reload=False):
    print(ident, LOADED_MODELS.keys())
    if not reload and ident in LOADED_MODELS:
        print(ident, "is already loaded")
        return LOADED_MODELS[ident]
    if tool is None:
        print("AUTO_LOAD seeking...")
        tool, mtype, date, extra = AUTO_LOAD[ident]
    # print(tool, mtype, date, extra)
    if date == "latest":
        print(LOCAL_MODELS[tool][mtype].keys())
        date = max(LOCAL_MODELS[tool][mtype].keys(),
                   key=lambda s: datetime.datetime.strptime(s, '%Y-%m-%d'))
    path = os.path.join(ROOT, tool, mtype, date)

    if tool == "continuousdoc2vec" and mtype == "model":
        model = continuousdoc2vecLoader(os.path.join(path, date))
    elif tool == "doc2vec" and mtype == "model":
        model = doc2vecLoader(os.path.join(path, date))
    elif tool == "doc2vec" and mtype == "knn":
        model, extra = [], "" if extra is None else extra
        filenames = sorted(filter(lambda name: extra in name,
                                  LOCAL_MODELS[tool][mtype][date]))
        # print(filenames)
        assert _KNN_DOC_REGEX[0].match(filenames[0])
        assert _KNN_DOC_REGEX[1].match(filenames[1])
        for filename in filenames:
            with open(os.path.join(path, filename), "rb") as file:
                model.append(joblib.load(file))
    elif tool == "text2phrase":
        assert extra in LOCAL_MODELS[tool][mtype][date]
        with open(os.path.join(path, extra), "rb") as file:
            model = joblib.load(file)
    elif tool == "wikifier" and mtype == "knn":
        model, extra = [], "" if extra is None else extra
        filenames = sorted(filter(lambda name: extra in name,
                                  LOCAL_MODELS[tool][mtype][date]))
        assert _KNN_WIK_REGEX[0].match(filenames[0])
        assert _KNN_WIK_REGEX[1].match(filenames[1])
        assert _KNN_WIK_REGEX[2].match(filenames[2])
        for filename in filenames:
            with open(os.path.join(path, filename), "rb") as file:
                model.append(joblib.load(file))
    elif tool == "tfidf" and mtype == "knn":
        model, extra = [], "" if extra is None else extra
        filenames = sorted(filter(lambda name: extra in name,
                                  LOCAL_MODELS[tool][mtype][date]))
        assert _KNN_TFIDF_REGEX[0].match(filenames[0])
        assert _KNN_TFIDF_REGEX[1].match(filenames[2])
        assert _KNN_TFIDF_REGEX[2].match(filenames[1])
        for filename in filenames:
            with open(os.path.join(path, filename), "rb") as file:
                model.append(joblib.load(file))
    elif tool == "tfidf" and mtype == "model":
        model = tfidfLoader(os.path.join(path, extra))
    elif tool == "ktss":
        print(GenerationGraph.available_format)
        model = GenerationGraph.load(path, GenerationGraph.available_format["Format.NetworkitBinary"])
    elif tool == "RNNordonator" and mtype == "model":
        model = c2v2orderLoader(os.path.join(path, "model.torch"))
    LOADED_MODELS[ident] = model
    return model


def load_models(load_settings, n_jobs=1):
    if n_jobs == -1:
        n_jobs = len(load_settings)
    if n_jobs == 1:
        [load_model(k, *v) for k, v in load_settings.items()]
    else:
        with joblib.Parallel(n_jobs=n_jobs) as pool:
            pool([joblib.delayed(load_model)(k, *v) for k, v in load_settings.items()])
    return LOADED_MODELS
