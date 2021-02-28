# # %%
# import sys
# print(sys.path)
# # %%
# import os
# import datetime
# import numpy as np
# import multiprocessing
# from wikification import _sum_page_rank, _recompute_on_anchor_text, _extraxt_concepts_from_wikires, _call_wikifier, _sum_classic_page_rank
# # %%
# import os
# import datetime
# corpuspath = "../../all_text_transcriptions/"
# directory = os.scandir(corpuspath)
# directory = list(directory)
#
# def __get_text(alltexts, file):
#     with open(file.path, "r") as f:
#         text = "".join(f.readlines())
#         alltexts.append(text)
#
# manager = multiprocessing.Manager()
# alltexts = manager.list()
# jobs = [multiprocessing.Process(target=__get_text, args=(alltexts, file)) for file in directory[:100]]
# _ = [p.start() for p in jobs]
# _ = [p.join() for p in jobs]
#
# alltexts = list(alltexts)
# # %%
# texts = filter(lambda text: len(text) > 10000, alltexts)
# text = next(texts)
# # print(text)
# print("sum_page_rank:")
# print([(c["title"], c["pageRank"]) for c in _sum_page_rank(text)][:10])
# print("recompute_on_anchor_text:")
# print([(c["title"], c["pageRank"]) for c in _recompute_on_anchor_text(text)][:10])
# # %%
# texts = list(filter(lambda text: len(text) < 10000 and len(text) > 200, alltexts))
# res = {"missed": {"f_sum_page_rank": [], "f_recompute_on_anchor_text": []},
#        "new": {"f_sum_page_rank": [], "f_recompute_on_anchor_text": []}}
#
# def n_diff_concepts(gt, xp):
#     gt, xp = set(c["url"] for c in gt), set(c["url"] for c in xp)
#     missed = len(gt - xp)
#     new = len(xp - gt)
#     return dict(missed=missed, new=new)
#
# for i, text in enumerate(texts):
#     print(i + 1, "/", len(texts))
#     groundtruth = _extraxt_concepts_from_wikires(_call_wikifier(text))
#     for method in [_recompute_on_anchor_text, _sum_page_rank]:
#         xp = method(text, bunchs_settings=dict(chunk_size=100, window_seek=10))
#         compare = n_diff_concepts(groundtruth, xp)
#     for feature in ["missed", "new"]:
#         res[feature][f"f_{method.__name__}"].append(compare[feature])
#
# print(f"On {len(texts)} texts")
# for method in [_recompute_on_anchor_text, _sum_page_rank]:
#     print(f"{method.__name__} result")
#     for feature in ["missed", "new"]:
#         vals = res[feature][f"f_{method.__name__}"]
#         print(f"avg_{feature}:{np.mean(vals)}")
#         print(f"std_{feature}:{np.std(vals)}")
#         print(f"sum_{feature}:{sum(vals)}")
# %%
import pprint
import time
import os
import datetime
import numpy as np
import multiprocessing
from wikification import _sum_page_rank, _recompute_on_anchor_text, _extraxt_concepts_from_wikires, _call_wikifier, _sum_classic_page_rank, _get_chunks
# path = "../../../predict-series/res/YaleSeriesCorpus/20-The_Early_Middle_Ages,_284–1000-Paul_Freedman/578-Transformation_of_the_Roman_Empire"
path = "../../../predict-series/res/YaleSeriesCorpus/32-Capitalism:_Success,_Crisis,_and_Reform-Douglas_W._Rae/882-Policy_Targets_for_Capitalist_Development"
print(multiprocessing.cpu_count())
with open(os.path.join(path, "rawtext"), "r") as f:
    text = " ".join(f.readlines())

# print("*" * 10)
# print("test __call_wikifier")
# start_time = time.time()
# res1 = _call_wikifier(text[:10000])
# elapsed_time = time.time() - start_time
# print(f"elapsed time: {elapsed_time:.2f} seconds")

# print("*" * 10)
# print("_sum_classic_page_rank")
# start_time = time.time()
# res2 = _sum_classic_page_rank(text)
# elapsed_time = time.time() - start_time
# print(f"elapsed time: {elapsed_time:.2f} seconds")

# print("*" * 10)
# print("_recompute_on_anchor_text")
# start_time = time.time()
# res3 = _recompute_on_anchor_text(text)
# elapsed_time = time.time() - start_time
# print(f"elapsed time: {elapsed_time:.2f} seconds")

print("*" * 10)
print("_sum_page_rank")
start_time = time.time()
res4 = _sum_page_rank(text)
elapsed_time = time.time() - start_time
print(f"elapsed time: {elapsed_time:.2f} seconds")
