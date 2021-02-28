from components.dataconnection.index import get_resource_description, get_experimental_features
from components.datamanip.duplicates import checkrmv_duplicates
from x5gonwp3tools.tools.difficulty.difficulty import __wpm, wikification2con_per_sec, tfidf2technicity
import requests
import datetime
from SETTINGS import EXP_IDS


experiment_id_doc2vec = EXP_IDS['doc2vec']['V1']['experiment_id']
experiment_id_text2tfidf = EXP_IDS['text2tfidf']['[1-2]-grams']['experiment_id']
experiment_id_wikifier = EXP_IDS['wikifier']['SIMPLE']['experiment_id']
model_type = "wikifier"


def get_resource_modelsdshsearch(search_infos):
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
                      max_resources=search_infos.get('max_resources', 20),
                      max_concepts=search_infos.get('max_concepts', 20),
                      page='1')
    search_e_s = "text={text}&type={type}&page={page};"

    # Execute X5GON search endpoint
    response = requests.get(PLATFORM_URL + search_endpoint.format(search_e_s.format(**search_e_p)))
    r_json = response.json()

    # Return modelsdsh needed output format
    resources_ids = [d['material_id'] for d in r_json['rec_materials'][:search_e_p['max_resources']]]
    # disc_rsltndvcts = {x['id']: x['result']['value'] for x in get_experimental_features(resources_ids,
    #                                                                                     [globals()[f"experiment_id_{model_type}"]],
    #                                                                                     order_needed=False)}
    # res_set, vects_set = zip(*((x, disc_rsltndvcts.get(x, {})) for x in resources_ids if x in disc_rsltndvcts))
    # res_set, vects_set = list(res_set), list(vects_set)
    disc_rsltfd = checkrmv_duplicates(resources_ids, model_type)
    resources_ids = disc_rsltfd[:search_e_p['max_resources']]
    resources_needed_infos = get_resource_description(resources_ids,
                                                      {"concepts": EXP_IDS['wikifier']['SIMPLE']['experiment_id'],
                                                       "keywords": EXP_IDS['text2tfidf']['SIMPLE']['experiment_id']},
                                                       max_concepts=search_e_p['max_concepts'],
                                                       max_keywords=search_e_p['max_concepts'])
    resources_final_infos = []
    for i, rid in enumerate(resources_ids):
        res_infos = resources_needed_infos.get(int(rid), dict())
        if res_infos:
            res_infos['duration'] = 60 * (res_infos['len_word'] / __wpm()["Slide"])
            res_infos['difficulty'] = wikification2con_per_sec(res_infos['len_char'], res_infos['len_concepts'])
            # res_infos['difficulty'] = tfidf2technicity( res_infos['keywords_full'] )
            del res_infos['keywords_full']
            del res_infos['wikifier_full']
            resources_final_infos.append(res_infos)
    return {'result': resources_final_infos}
