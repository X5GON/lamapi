from components.dataconnection.index import (get_grpa_fredata_x5disc,
                                             get_resource_description,
                                             get_resource_metadata,
                                             get_grpa_fredata_x5rec,
                                             get_plgn_instancedata,
                                             update_plgn_x5rec,
                                             get_experimental_features)
from components.datamanip.duplicates import checkrmv_duplicates
from x5gonwp3tools.tools.difficulty.difficulty import __wpm, wikification2con_per_sec
from services.distance.wikifier.knn.core import knn_wikifier_text, knn_wikifier_list
from services.distance.doc2vec.knn.core import knn_doc2vec_text, knn_doc2vec_list
from services.distance.text2tfidf.knn.core import knn_tfidf_text
from services.distance.wikifier.knn.core import knn_wikifier_res
from services.distance.doc2vec.knn.core import knn_doc2vec_res
from services.distance.text2tfidf.knn.core import knn_tfidf_res
from SETTINGS import EXP_IDS
from utils import time_usage

import string
import itertools
from operator import itemgetter
from time import time
import traceback
import time as temptime
import requests


experiment_id_doc2vec = EXP_IDS['doc2vec']['V1']['experiment_id']
experiment_id_text2tfidf = EXP_IDS['text2tfidf']['[1-2]-grams']['experiment_id']
experiment_id_wikifier = EXP_IDS['wikifier']['SIMPLE']['experiment_id']
model_type = "wikifier"


# Build the mbz from the plalist
def get_mdlplgnfre_data(freobj_infos):
    return switch_fres(freobj_infos)


def switch_fres(freobj: object):
    switcher = {
        "x5discovery": lambda: compute_frepditems_x5disc(freobj),
        "x5recommend": lambda: compute_frepditems_x5rec(freobj)
    }
    return switcher.get(freobj['fre'], {"result": "failed",
                                        "rltdetails": "no feature found with this name",
                                        "actions": "nothing",
                                        "pddata": []}
                        )()


@time_usage
def compute_frepditems_x5disc(freobj_infos):
    try:
        grpa_disc = get_grpa_fredata_x5disc(freobj_infos)
        rked_grpa_disc = rank_grpa_fredata_x5disc(grpa_disc)
        return {"result": "success",
                "rltdetails": "",
                "actions": "update ui",
                "pddata": rked_grpa_disc}
    except KeyError as e:
        print(e)
        return {"result": "failed",
                "rltdetails": "error getting feature data",
                "actions": "nothing",
                "pddata": []}


def rank_grpa_fredata_x5disc(grpa_disc):
    for i, sq in enumerate(grpa_disc):
        sq["rksearch"] = int(sq['nbsearch']) * compute_trendiness_frltoftsp(sq['tspsearch'].split(","))
    rked_grpa = sorted(grpa_disc, key=itemgetter('rksearch'), reverse=True)
    return rked_grpa


# Trendiness score: computed based on unixtimestamp:: smaller the score is, more recent the event is
def compute_trendiness_frltoftsp(ltoftsps):
    return 1 + sum([1/(lambda x: float(int(time()) - int(x)) if float(int(time()) - int(x)) != 0 else float(1))(tsp) for tsp in ltoftsps if tsp != ''])


@time_usage
def rank_grpa_fredata_x5rec(x5_recs, freobj_infos):
    # Get all neighbors of the initial list
    try:
        neigs_knns = compute_knn_forx5recitems(x5_recs, model_type, freobj_infos)

        # Intersection between lists done to avoid having res without knn (can block the algo)
        neigs_set = list(set(list(itertools.chain.from_iterable([ngknn['knn'] for ix, ngknn in neigs_knns.items()])) + list(set(x5_recs).intersection(list(neigs_knns.keys())))))
        # Remove duplicates if exists whithin the set of resources
        neigs_set = checkrmv_duplicates(neigs_set, model_type)
        # Get all grpa of the neigs set
        grpa_neigs = get_grpa_fredata_x5rec(freobj_infos, spec_res=neigs_set)
        not_rked_grpa = []
        for i, neig in enumerate(neigs_set):
            res_grpa_f = grpa_neigs.get(neig, {"oerid": neig,
                                               "nbacess": 0,
                                               "tspacess": ""})
            # distance score over the knns in which the res is there pondered by their trendiness scores
            res_grpa_f["rkacess"] = sum([
                                          sum([
                                                1/res[1] * compute_trendiness_frltoftsp(grpa_neigs.get(res[0], {"oerid": res[0], "nbacess": 0, "tspacess": ""})['tspacess'].split(","))
                                                if neig == res[0] and res[1] != 0 else 0 for res in zip(knn['knn'], knn['knndists'])
                                              ])
                                          for ix, knn in neigs_knns.items()]
                                        )
            not_rked_grpa.append(res_grpa_f)
        rked_grpa = sorted(not_rked_grpa, key=itemgetter('rkacess'), reverse=True)[:freobj_infos['max_pdres']]
        # print(not_rked_grpa)
        # print(rked_grpa)
    except KeyError as e:
        print(e)
        print(traceback.format_exc())
        # input("hello !")
        return []
    return rked_grpa


@time_usage
def compute_frepditems_x5rec(freobj_infos):
    try:
        x5_recs = compute_actual_x5recitems(freobj_infos, model_type)
        x5_grpa_recs = []
        # method 2: based on the knns of the first list provided by the recommender aggregated by trendiness score
        x5_grpa_recs = rank_grpa_fredata_x5rec(x5_recs, freobj_infos)
        x5_grpa_recsids = [res['oerid'] for res in x5_grpa_recs]
        update_plgn_x5rec(freobj_infos, {}, x5reconly=True, x5reclast=x5_grpa_recsids)
        return {"result": "success",
                "rltdetails": "",
                "actions": "update ui",
                "pddata": enrich_pd_resources(x5_grpa_recsids)[:freobj_infos['max_pdres']],
                "rkdata": x5_grpa_recs}
    except KeyError as e:
        print(e)
        print(traceback.format_exc())
        return {"result": "failed",
                "rltdetails": "error getting feature data",
                "actions": "nothing",
                "pddata": [],
                "rkdata": []}


@time_usage
def compute_actual_x5recitems(freobj_infos, model_type):
    # #1st method
    # rec_text = " ".join(freobj_infos['grpgcrta_data'].values())
    # knn = globals()[f"knn_{model_type}_text"](resource_text=rec_text,
    #                                           return_dist=True,
    #                                           remove_duplicates=True,
    #                                           n_neighbors=freobj_infos['max_pdres'])
    # return knn['neighbors']
    # #2nd method
    last_rec = get_plgn_instancedata(freobj_infos)
    last_reclist = []
    if 'lastlst' in last_rec and 'lastlst' != '':
        last_reclist = (last_rec['lastlst']).split(',')
    else:
        initinfos = init_x5rec(freobj_infos, last_rec)
        last_reclist = initinfos['lastlst']
        # update x5rec settingsdata (don't forget to update after recompute x5recs)
        update_plgn_x5rec(freobj_infos, initinfos['x5rec'])
    return list(map(int, last_reclist))


@time_usage
def init_x5rec(freobj_infos, last_rec):
    if 'initlst' in last_rec and last_rec['initlst'] != '':
        return {'x5rec': {'initstr': last_rec['initstr'],
                          'initlst': last_rec['initlst'],
                          'lastlst': last_rec['initlst']
                          },
                'lastlst': (last_rec['initlst']).split(',')
                }
    else:
        initfromx5disc = search_usingx5disc({'q': freobj_infos['grpgcrta_data']['modx5init'],
                                             'max_resources': 10,
                                             'max_concepts': 5
                                             })
        return {'x5rec': {'initstr': freobj_infos['grpgcrta_data']['modx5init'],
                          'initlst': ','.join(map(str, initfromx5disc)),
                          'lastlst': ','.join(map(str, initfromx5disc))
                          },
                'lastlst': initfromx5disc
                }


@time_usage
def search_usingx5disc(search_infos):
    # The X5GON API is available at:
    PLATFORM_URL = "https://platform.x5gon.org/api/v1"
    # initialise the endpoint
    search_endpoint = "/search?{}"

    # search_endpoint parameters
    search_e_p = dict(text=search_infos['q'] if 'q' in search_infos else '',
                      type=",".join(search_infos['type']) if 'type' in search_infos else '',
                      provider=",".join(map(str, search_infos.get('provider', []))),
                      orig_lang=",".join(map(str, search_infos.get('orig_lang',[]))),
                      available_langs=",".join(map(str, search_infos.get('available_langs',[]))),
                      max_resources=search_infos.get('max_resources', 10)*2,
                      max_concepts=search_infos.get('max_concepts', 5),
                      page='1')
    search_e_s = "text={text}&type={type}&page={page};"

    # Execute X5GON search endpoint
    response = requests.get(PLATFORM_URL + search_endpoint.format(search_e_s.format(**search_e_p)))
    r_json = response.json()

    # Return modelsdsh needed output format
    disc_rslt = [d['material_id'] for d in r_json['rec_materials']]
    # disc_rsltndvcts = {x['id']: x['result']['value'] for x in get_experimental_features(disc_rslt,
    #                                                                                     [globals()[f"experiment_id_{model_type}"]],
    #                                                                                     order_needed=False)}
    # res_set, vects_set = zip(*((x, disc_rsltndvcts.get(x, {})) for x in disc_rslt if x in disc_rsltndvcts))
    # res_set, vects_set = list(res_set), list(vects_set)
    disc_rsltfd = checkrmv_duplicates(disc_rslt, model_type)
    return [d for d in disc_rsltfd[:search_e_p['max_resources']]]


@time_usage
def compute_knn_forx5recitems(rec_items, model_type, freobj_infos):
    rec_items_knn = {}
    rec_items_knnuu = globals()[f"knn_{model_type}_list"](res_ids=rec_items,
                                                          return_dist=True,
                                                          remove_duplicates=True,
                                                          n_neighbors=freobj_infos['max_pdres']/3)
    rec_items_knn = {rec_items[i]: dict(knn=v,
                                        knndists=rec_items_knnuu['distances'][i]) for i, v in enumerate(rec_items_knnuu['neighbors'])}
    return rec_items_knn


def sing_knn(item, model_type, freobj_infos):
    start = temptime.perf_counter()
    knn = globals()[f"knn_{model_type}_res"](resource_id=item,
                                             return_dist=True,
                                             remove_duplicates=True,
                                             n_neighbors=freobj_infos['max_pdres']/3)
    end = temptime.perf_counter()
    print("elapsed time: (%s) %f ms" % ("sing_knn", 1000*(end - start)))
    return {"item": item,
            "knn": knn['neighbors'],
            "knndists": knn['distances']}


@time_usage
def enrich_pd_resources(pd_resources):
    resources_needed_infos = get_resource_description(pd_resources,
                                                      {"concepts": EXP_IDS['wikifier']['SIMPLE']['experiment_id'],
                                                       "keywords": EXP_IDS['text2tfidf']['SIMPLE']['experiment_id']},
                                                       max_concepts=5,
                                                       max_keywords=5)
    res_metadata = get_resource_metadata(pd_resources)
    resources_final_infos = []
    for i, rid in enumerate(pd_resources):
        res_infos = resources_needed_infos.get(int(rid), dict())
        res_metainfos = res_metadata.get(int(rid), dict())
        # The avoid exeception on not found ids taken/computed by rec_algo from models files (res_infos/res_metadata)
        try:
            if res_infos or res_metainfos:
                if res_infos:
                    res_infos['difficulty'] = wikification2con_per_sec(res_infos['len_char'], res_infos['len_concepts']) if ('len_char' in res_infos and res_infos['len_char'] != 0) else 0
                    if 'keywords_full' in res_infos:
                        del res_infos['keywords_full']
                    if 'wikifier_full' in res_infos:
                        del res_infos['wikifier_full']
                    res_infos['concepts'] = res_infos['wikifier'] if 'wikifier' in res_infos else []
                else:
                    # In case there is no info returned from exp_results query
                    res_infos['id'] = res_metainfos['id']
                    res_infos['orig_lang'] = res_metainfos['orig_lang']
                    res_infos['provider'] = res_metainfos['provider']
                    res_infos['difficulty'] = ''
                    res_infos['keywords'] = []
                    res_infos['concepts'] = []
                res_infos['title'] = res_metainfos['title'] if res_metainfos['title'] is not None else ''
                res_infos['description'] = ' '.join(res_metainfos['description'].split()[:150]) if res_metainfos['description'] is not None else ''
                res_infos['duration'] = f"~ {res_metainfos['len_word'] / __wpm()['Slide']} mins"
                res_infos['url'] = res_metainfos['url']
                res_infos['author'] = ", ".join(res_metainfos['authors']) if res_metainfos['authors'] is not None else ''
                res_infos['date'] = res_metainfos['date'] if res_metainfos['date'] != '' else ''
                res_infos['mediatype'] = res_metainfos['type']
                res_infos['mimetype'] = res_metainfos['mimetype']
                res_infos['license'] = res_metainfos['license'] if res_metainfos['license'] is not None else ''
                # This is to make sure that there is no "" chars can brake the xmls
                res_infos['title'] = ''.join(filter(lambda x: x in string.printable, res_infos['title'].replace('"',"")))
                res_infos['description'] = ''.join(filter(lambda x: x in string.printable, res_infos['description'].replace('"',"")))
        except KeyError as e:
            print(e)
            print(traceback.format_exc())
        resources_final_infos.append(res_infos)
    return resources_final_infos
