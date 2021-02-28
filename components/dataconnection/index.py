import json
import operator
import pandas as pd
from heapq import nlargest
from typing import Dict, List
from utils import time_usage, get_args
import psycopg2
from psycopg2.extras import DictCursor, execute_values

from x5gonwp3tools.tools.difficulty.difficulty import tfidf2technicity


class DBConnection:

    __instance = None
    # Default DevDB PG Credentials
    args = get_args()
    __credentials = {"pghost": args.dbhost,
                     "pgdatabase": args.dbname,
                     "pguser": args.dbuser,
                     "pgpassword": args.dbpass,
                     "pgport": args.dbport}

    @property
    def credentials(self):
        return self.credentials

    @staticmethod
    def getInstance():
        """ Static access method. """
        if DBConnection.__instance is None:
            DBConnection()
        return DBConnection.__instance

    @staticmethod
    def __db_connect(pghost: str,
                     pgdatabase: str,
                     pguser: str,
                     pgpassword: str,
                     pgport: str):
        # Set up a connection to the postgres server.
        conn_string = f"host={pghost} \
                        port={pgport} \
                        dbname={pgdatabase} \
                        user={pguser} \
                        password={pgpassword}"
        conn = psycopg2.connect(conn_string)
        conn.set_session(autocommit=True)
        return conn

    def __init__(self):
        """ Virtually private constructor. """
        if DBConnection.__instance is None:
            DBConnection.__instance = DBConnection.__db_connect(**DBConnection.__credentials)
        else:
            raise Exception("This class is a singleton!")


DEFAULT_BATCH_SIZE = 1000


def batching(functor):
    def wrapper(resource_ids: List,
                *args,
                **kwargs):
        batch_size = DEFAULT_BATCH_SIZE
        previ, nexti = 0, batch_size
        while previ + batch_size < len(resource_ids):
            cursor = functor(resource_ids[previ: nexti],
                             *args,
                             **kwargs)
            for res in cursor:
                yield res
            previ = nexti
            nexti += batch_size
        if previ < len(resource_ids):
            cursor = functor(resource_ids[previ:],
                             *args,
                             **kwargs)
            for res in cursor:
                yield res
    return wrapper


@time_usage
def get_searchresults_forlamdash(**kwargs):
    query = "SELECT {_select} FROM {_from} WHERE {_where};"
    values = dict(_select="t0.id as id, \
                           title, \
                           authors as author, \
                           name as provider, \
                           domain, \
                           url",
                  _from="oer_materials t0 \
                         INNER JOIN urls t2 \
                         ON t0.id=t2.material_id \
                         INNER JOIN providers t1 \
                         ON t2.provider_id=t1.id \
                         INNER JOIN experiment_results t3 \
                         ON t0.id=t3.record_id",
                  _where=f"title LIKE '%{str(kwargs['search'])}%' \
                           AND experiment_id=5")
    if kwargs['use_model']:
        values["_from"] = values["_from"].replace(' INNER JOIN experiment_results t3\
                                                    ON t0.id=t3.record_id', '')
        values["_where"] = f"t0.id in ({' ,'.join(map(str, kwargs['resource_ids']))})"
    with DBConnection.getInstance().cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute(query.format(**values))
        for x in cursor:
            yield x


@time_usage
def get_transcription_forlamdash(params: Dict[str, List]) -> str:
    # Get only Orig+English trans for lamdash
    transcriptions = {params['langorig']: '', 'en': ''}
    query = f"SELECT language, value ->> 'value' \
              FROM material_contents where material_id={params['resource']}\
              AND language IN ('en', '{params['langorig']}')\
              AND extension='plain';"
    with DBConnection.getInstance().cursor() as cursor:
        cursor.execute(query)
        for record in cursor:
            transcriptions[record[0]] = record[1]
    return transcriptions


@time_usage
def get_metrics_bounds_forlamdash(resource_neighbors):
    bounds = {
        "difficulty": {
            "min": 0,
            "max": 0
        },
        "length":     {
            "min": 0,
            "max": 0
        },
    }
    for r in resource_neighbors.values():
        diff = float(r['technicities'])
        leng = int(r['length'])
        if diff > bounds['difficulty']['max']:
            bounds['difficulty']['max'] = diff
        if diff < bounds['difficulty']['min']:
            bounds['difficulty']['min'] = diff
        if leng > bounds['length']['max']:
            bounds['length']['max'] = leng
        if leng < bounds['length']['min']:
            bounds['length']['min'] = leng
    return bounds


@time_usage
def fetch_resources_datafromdb_forlamdash(knn, remove_unfound_res_indb=True):
    # Get metadata
    resources_ids = knn["neighbors"]
    recordforresmetadata = get_experimental_metadatas(resources_ids)
    # Get av-langs
    recordforavailablelangs = get_experimental_contents(resources_ids)
    # Tfidf + wikifier
    # idtfidf = EXP_IDS['text2tfidf']['SIMPLE']['experiment_id']
    # idwik = EXP_IDS['wikifier']['SIMPLE']['experiment_id']
    idtfidf = 16
    idwik = 12

    recordforneededfeatures = get_experimental_features(
        resource_ids=resources_ids, experiment_ids=[idtfidf, idwik])

    resources_info = {}
    for i, rid in enumerate(resources_ids):
        resources_info[rid] = {"technicities": 0,
                               "length": '0',
                               "keywords": [],
                               "wikifier": [],
                               "reduction_coordinates": knn["projected_matrix"][i],
                               "in_db": 0}
    # Return needed features
    for res in recordforneededfeatures:
        rid = res["id"]
        resource_info = resources_info.get(rid, {})
        if res["experiment_id"] == idtfidf:
            resource_info["keywords"] = nlargest(10,
                                                 res["result"]['value'].items(),
                                                 operator.itemgetter(1))
            resource_info["technicities"] = tfidf2technicity(res["result"]['value'])
        elif res["experiment_id"] == idwik:
            resource_info["wikifier"] = nlargest(10,
                                                 ((sres["title"],
                                                   sres["url"],
                                                   sres["pageRank"],
                                                   sres["cosine"]
                                                   ) for sres in res["result"]['value']["concepts"]),
                                                 operator.itemgetter(2))
        else:
            raise RuntimeError("Unexpected experiment_id")
        resources_info[rid] = resource_info
    # Return needed language/trans informations
    for res in recordforavailablelangs:
        rid = res["id"]
        resource_info = resources_info.get(rid, {})
        resource_info['available_langs'] = resource_info.get(
            'available_langs', []) + [res["language"]]
        resource_info['length'] = str(res["value"])
        resources_info[rid] = resource_info
    # Return needed meta-data
    for res in recordforresmetadata:
        rid = res["id"]
        resource_info = resources_info.get(rid, {})
        # Set the flag only if the resource is existing in the database
        resource_info['in_db'] = 1
        resource_info.update(**dict(author=res["authors"],
                                    category='',
                                    date=str(res["creation_date"]),
                                    duration='',
                                    filename=res["id"],
                                    id=res["id"],
                                    img='',
                                    license=res["license"],
                                    orig_lang=res["language"],
                                    part='',
                                    provider=res["provider"],
                                    slug=res["id"],
                                    # technicities= 0,
                                    title=res["title"],
                                    type=res["type"],
                                    url=res["url"]))
    print(list(map(lambda d: (d[0], d[1]["title"]), resources_info.items())))
    print(list(map(lambda d: (d[0], d[1]["url"]), resources_info.items())))
    print(list(map(lambda d: (d[0], d[1]["type"]), resources_info.items())))
    print(list(map(lambda d: (d[0], d[1]["title"]), resources_info.items())))
    print(list(map(lambda d: (d[0], d[1]["author"]), resources_info.items())))
    print("Eliminated because not found in DB:", [k for (k, v) in resources_info.items() if v['in_db'] == 0])
    resources_info = {k: dict(filter(lambda x: x[0] != 'in_db', list(v.items())))  for (k, v) in resources_info.items() if v['in_db'] == 1}
    return resources_info


# @batching
@time_usage
# These functions to be used to fetch the meta-data of a list of resources (title..., content infos) in case
# there is no concepts/keywords computed
def get_resource_metadata(resource_ids: List):
    resource_needed_infos = get_resource_neededmetadata(resource_ids)
    resource_formatted_infos = {}
    for val in resource_needed_infos:
        if val['id'] not in resource_formatted_infos:
            resource_formatted_infos[val['id']] = {
                                                    'id': val['id'],
                                                    'title': val['title'],
                                                    'authors': val['authors'],
                                                    'provider': val['provider'],
                                                    'url': val['url'],
                                                    'thumbnail': '',
                                                    'type': val['type'],
                                                    'mimetype': val['mimetype'],
                                                    'len_char': 0,
                                                    'len_word': 0,
                                                    'len_concepts': 0,
                                                    'duration': 0,
                                                    'available_langs': [].append(val['trans_lang']),
                                                    'orig_lang': val['language'],
                                                    'date': val['creation_date'].replace(tzinfo=None).isoformat(' ') if val['creation_date'] is not None else '',
                                                    'license': val['license'],
                                                    'description': '',
                                                    'difficulty': 0
                                                    }
        if (val["trans_ext"] == "plain" and val["trans_lang"] == "en") or (val["trans_ext"] == "plain" and val["trans_lang"] == val['language']):
            if val['description'] == '' or val['description'] is None:
                if resource_formatted_infos[val['id']]['description'] == '':
                    resource_formatted_infos[val['id']]['len_char'] = val['trans_length_char']
                    resource_formatted_infos[val['id']]['len_word'] = val['trans_len_word']
                    resource_formatted_infos[val['id']]['description'] = val['trans_slot']
            else:
                resource_formatted_infos[val['id']]['len_char'] = val['trans_length_char']
                resource_formatted_infos[val['id']]['len_word'] = val['trans_len_word']
                resource_formatted_infos[val['id']]['description'] = val['description']
    return dict(resource_formatted_infos)


@batching
@time_usage
def get_resource_neededmetadata(resource_ids):
    # Could be changed to be fetched from a 'view' containing all infos (must be tested level performance)!
    request = "SELECT {_select} FROM {_from} WHERE {_where};"
    fields = ["id", "title", "description", "authors", "language", "type", "mimetype", "creation_date", "retrieved_date", "cr_re_date", "license",
              "provider",
              "url",
              "trans_lang", "trans_length_char", "trans_len_word", "trans_ext", "trans_lang", "trans_slot"]
    values = dict(_select=f"t0.id, t0.title, t0.description, t0.authors, t0.language as lang, t0.type as type, t0.mimetype as mimetype, t0.creation_date, t0.retrieved_date, COALESCE(t0.creation_date, t0.retrieved_date, null) ,t0.license, \
                            t2.name as provider, \
                            t1.url, \
                            t4.language, CHAR_LENGTH(t4.value->>'value'), array_length(string_to_array(t4.value->>'value', ' '),1), t4.extension, t4.language, SUBSTRING(t4.value->>'value', 0, 1000)",
                  _from="oer_materials t0 \
                         full join urls t1 on t0.id=t1.material_id \
                         full join providers t2 on t1.provider_id=t2.id \
                         full join material_contents t4 on t0.id=t4.material_id",
                  _where=f"t0.id in ({' ,'.join(map(str, resource_ids))})")
    with DBConnection.getInstance().cursor() as cursor:
        cursor.execute(request.format(**values))
        # print("Debug3.3:",  request.format(**values))
        for val in cursor:
            yield dict(zip(fields, val))


@batching
@time_usage
def get_resource_neededinfos(resource_ids, experiment_ids):
    # Could be changed to be fetched from a 'view' containing all infos (must be tested level performance)!
    request = "SELECT {_select} FROM {_from} WHERE {_where};"
    fields = ["id", "title", "description", "authors", "language", "type", "mimetype", "creation_date", "retrieved_date", "cr_re_date", "license",
              "provider",
              "url",
              "record_id", "experiment_id", "results",
              "trans_lang", "trans_length_char", "trans_len_word", "trans_ext", "trans_lang", "trans_slot"]
    values = dict(_select=f"t0.id, t0.title, t0.description, t0.authors, t0.language as lang, t0.type as type, t0.mimetype as mimetype, t0.creation_date, t0.retrieved_date, COALESCE(t0.creation_date, t0.retrieved_date, null) ,t0.license, \
                            t2.name as provider, \
                            t1.url, \
                            t3.record_id, t3.experiment_id, t3.results, \
                            t4.language, CHAR_LENGTH(t4.value->>'value'), array_length(string_to_array(t4.value->>'value', ' '),1), t4.extension, t4.language, SUBSTRING(t4.value->>'value', 0, 1000)",
                  _from="oer_materials t0 \
                         full join urls t1 on t0.id=t1.material_id \
                         full join providers t2 on t1.provider_id=t2.id \
                         full join experiment_results t3 on t0.id=t3.record_id \
                         full join material_contents t4 on t0.id=t4.material_id",
                  _where=f"t3.record_id in ({' ,'.join(map(str, resource_ids))}) and t3.experiment_id in ({' ,'.join(map(str , [experiment_ids['concepts'], experiment_ids['keywords']]))})")
    with DBConnection.getInstance().cursor() as cursor:
        cursor.execute(request.format(**values))
        for val in cursor:
            yield dict(zip(fields, val))


# @batching
@time_usage
def get_resource_description(resource_ids: List,
                             experiment_ids: dict,
                             max_concepts: int = 20,
                             max_keywords: int = 20):
    resource_needed_infos = get_resource_neededinfos(resource_ids, experiment_ids)
    resource_thls = get_resource_thumbnail(resource_ids)
    resource_formatted_infos = {}
    for val in resource_needed_infos:
        if val['id'] not in resource_formatted_infos:
            resource_formatted_infos[val['id']] = {
                                                    'keywords_full': {},
                                                    'wikifier_full': {},
                                                    'id': 0,
                                                    'title': '',
                                                    'authors': '',
                                                    'provider': '',
                                                    'url': '',
                                                    'thumbnail': '',
                                                    'type': '',
                                                    'mimetype': '',
                                                    'len_char': 0,
                                                    'len_word': 0,
                                                    'len_concepts': 0,
                                                    'duration': 0,
                                                    'available_langs': [],
                                                    'orig_lang': '',
                                                    'date': '',
                                                    'license': '',
                                                    'description': '',
                                                    'difficulty': 0}
        if val["experiment_id"] == experiment_ids["concepts"]:
            resource_formatted_infos[val['id']]['len_concepts'] = len(val["results"]["value"]["concepts"]) if "concepts" in val["results"]["value"] else 0
            resource_formatted_infos[val['id']]['wikifier_full'] = val['results']
            resource_formatted_infos[val['id']]['wikifier'] = nlargest(max_concepts,
                                                                       ({"label": sres["title"],
                                                                         "url": sres["url"],
                                                                         "value": sres["norm_pageRank"]
                                                                         } for sres in val["results"]["value"]["concepts"]),
                                                                       key=lambda d: d["value"]) if "concepts" in val["results"]["value"] else []
        if val["experiment_id"] == experiment_ids["keywords"]:
            resource_formatted_infos[val['id']]['keywords'] = nlargest(max_keywords,
                                                                       ({"label": kres[0],
                                                                         "value": kres[1]} for kres in val["results"]["value_norm"].items()),
                                                                       key=lambda d: d["value"])
            resource_formatted_infos[val['id']]['keywords_full'] = val['results']
            resource_formatted_infos[val['id']]['id'] = val['id']
            resource_formatted_infos[val['id']]['title'] = val['title']
            resource_formatted_infos[val['id']]['authors'] = val['authors']
            resource_formatted_infos[val['id']]['provider'] = val['provider']
            resource_formatted_infos[val['id']]['url'] = val['url']
            resource_formatted_infos[val['id']]['thumbnail'] = 'http://x5learn.org/files/thumbs/' + resource_thls[val['id']]["images"] if resource_thls[val['id']]["images"] != '' else ''
            resource_formatted_infos[val['id']]['type'] = val['type']
            resource_formatted_infos[val['id']]['mimetype'] = val['mimetype']
            resource_formatted_infos[val['id']]['available_langs'].append(val['trans_lang']) if val['trans_lang'] not in resource_formatted_infos[val['id']]['available_langs'] else resource_formatted_infos[val['id']]['available_langs']
            resource_formatted_infos[val['id']]['orig_lang'] = val['language']
            resource_formatted_infos[val['id']]['date'] = val['creation_date'].replace(tzinfo=None).isoformat(' ') if val['creation_date'] is not None else ''
            resource_formatted_infos[val['id']]['license'] = val['license']
            resource_formatted_infos[val['id']]['difficulty'] = 0
        if val["trans_ext"] == "plain" and val["trans_lang"] == "en":
            resource_formatted_infos[val['id']]['len_char'] = val['trans_length_char']
            resource_formatted_infos[val['id']]['len_word'] = val['trans_len_word']
            if val['description'] == '' or val['description'] is None:
                resource_formatted_infos[val['id']]['description'] = val['trans_slot']
            else:
                resource_formatted_infos[val['id']]['description'] = val['description']
    return dict(resource_formatted_infos)


# To be replaced with direct access to x5learndb to fetch thumbnails data
@time_usage
def get_resource_thumbnail(resource_ids: List):
    # #Method 1: from dump file
    # To be used only to regenerate lighter version of thumbnails dump
    # #gene_tsvfrom_thumnailsdump()
    # print(datetime.datetime.now())
    # x5ln_ctlgue_ltuu = pd.read_csv("rawdata/thumbnails/thls_lt.tsv",
    #                                sep="\t",
    #                                index_col=0).fillna('')
    # fl_reslist = {int(x): {"material_id": str(x5ln_ctlgue_ltuu['material_id'].get(x, x)),
    #                        "images": (x5ln_ctlgue_ltuu['images'].get(x, ''))} for x in resource_ids}
    # print(datetime.datetime.now())
    # #Method 2: from x5learn_db
    # print((DBConnection.getInstance()).get_dsn_parameters())
    pgconparams = vars(DBConnection)['_DBConnection__credentials']
    query = f"SELECT case \
              when ('conth' <> ALL (dblink_get_connections()) or dblink_get_connections() IS NULL) then (SELECT dblink_connect_u('conth', 'user={pgconparams['pguser']} password={pgconparams['pgpassword']} dbname=x5learn_v1')) \
              end as run_status; \
              SELECT * \
              from dblink( \
                'conth', \
                'select data->''material_id'', data->''images'' from oer \
                 where (data->>''material_id'')::int in ({','.join(list(map(str, resource_ids)))})' \
              ) as t1(id text, img text);"
    with DBConnection.getInstance().cursor() as cursor:
        cursor.execute(query)
        pdres = {}
        for val in cursor:
            pdres[val[0]] = {"material_id": str(val[0]),
                             "images": eval(val[1])[0] if len(eval(val[1])) > 0 else ''}
    fl_reslist = {int(x): pdres.get(str(x), {"material_id": str(x),
                                             "images": ''
                                             }) for x in resource_ids}
    return fl_reslist


# To be replaced with direct access to x5learndb to fetch thumbnails data
def gene_tsvfrom_thumnailsdump():
    dict_parser = lambda x: dict(eval(x))
    x5ln_rawctlgue = pd.read_csv("rawdata/thumbnails/thls.tsv",
                                 sep="\t",
                                 converters={'data': dict_parser})
    x5ln_clnctlgue = {}
    x5ln_clnctlgue = {x["material_id"]: {"material_id": x["material_id"],
                                         "images": (x["images"][0] if len(x["images"]) > 0 else '')} for x in x5ln_rawctlgue["data"]}
    x5ln_clnctlgue_lght = pd.DataFrame.from_dict(x5ln_clnctlgue, orient='index').fillna(0)
    x5ln_clnctlgue_lght.to_csv("rawdata/thumbnails/thls_lt.tsv", sep="\t")


@batching
@time_usage
def get_experimental_features(resource_ids: List,
                              experiment_ids: List,
                              order_needed: bool = False) -> object:
    query = "SELECT {_select} FROM {_from} WHERE {_where};"
    if order_needed:
        query = query.replace(";", " ORDER BY {_order};")
    values = dict(_select="record_id as id, experiment_id, results as result",
                  _from="experiment_results t0",
                  _where=f"record_id in ({' ,'.join(map(str, resource_ids))}) \
                           AND experiment_id in ({' ,'.join(map(str , experiment_ids))})")
    if order_needed:
        values["_order"] = "".join([f"t0.record_id={record_id}," for record_id in reversed(resource_ids)])[:-1]
    with DBConnection.getInstance().cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute(query.format(**values))
        for x in cursor:
            yield x


@batching
@time_usage
def get_experimental_metadatas(resource_ids: List,
                               order_needed: bool = False) -> object:
    query = "SELECT {_select} FROM {_from} WHERE {_where};"
    if order_needed:
        query = query.replace(";", " ORDER BY {_order};")
    values = dict(_select=f"t0.id as id,\
                            title,\
                            description,\
                            authors,\
                            t0.language as language,\
                            t0.type as type, creation_date,\
                            retrieved_date,\
                            name as provider,\
                            license,\
                            t2.url as url",
                  _from="oer_materials t0 full join urls t2 on t0.id=t2.material_id full join providers t1 on t2.provider_id=t1.id",
                  _where=f"t0.id in ({' ,'.join(map(str, resource_ids))})")
    if order_needed:
        values["_order"] = "".join([f"t0.material_id={record_id}," for record_id in reversed(resource_ids)])[:-1]
    with DBConnection.getInstance().cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute(query.format(**values))
        for x in cursor:
            yield x


@batching
@time_usage
def get_experimental_contents(resource_ids: List,
                              order_needed: bool = False,
                              return_content_raw: bool = False,
                              ) -> object:
    query = "SELECT {_select} FROM {_from} WHERE {_where};"
    if order_needed:
        query = query.replace(";", " ORDER BY {_order};")
    values = dict(_select="t0.material_id as id,\
                           t0.language as language,\
                           CHAR_LENGTH(value->>'value') as value",
                  _from="material_contents t0",
                  _where=f"t0.material_id in ({' ,'.join(map(str, resource_ids))}) \
                           AND t0.extension ='plain' and t0.language='en'")
    if order_needed:
        values["_order"] = "".join([f"t0.material_id={record_id}," for record_id in reversed(resource_ids)])[:-1]
    if return_content_raw:
        values['_select'] += ", value->>'value' as content_raw"
    with DBConnection.getInstance().cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute(query.format(**values))
        for x in cursor:
            yield x


def get_all_resource_ids() -> list:
    # To be replaced then by the fetch from DB/API....
    query = f"SELECT distinct oer_materials.id \
              FROM oer_materials \
              INNER JOIN material_contents t0 \
              ON oer_materials.id=t0.material_id \
              WHERE t0.language='en' and extension='plain';"
    with DBConnection.getInstance().cursor() as cursor:
        cursor.execute(query)
        for x in map(operator.itemgetter(0), cursor):
            yield x


def get_all_computed_resource_ids(experiment_id: int) -> list:
    # To be replaced then by the fetch from DB/API....
    # Another parameter must be added to specify which 'content' to be rendered(orig, traduction...)
    query = f"SELECT distinct experiment_results.record_id \
              FROM experiment_results \
              WHERE experiment_results.experiment_id={str(experiment_id)};"
    with DBConnection.getInstance().cursor() as cursor:
        cursor.execute(query)
        for x in map(operator.itemgetter(0), cursor):
            yield x


def get_experiment_results(experiment_id,
                           specific_fields=["value"]) -> (list, list):
    query = f"SELECT record_id, results as value \
              FROM experiment_results \
              WHERE experiment_id={str(experiment_id)} ;"
    with DBConnection.getInstance().cursor() as cursor:
        cursor.execute(query)
        rids, vectors = [], []
        for rid, v in cursor:
            try:
                for spec in specific_fields:
                    v = v[spec]
                rids.append(rid)
                vectors.append(v)
            except KeyError as e:
                if "error" not in v:
                    raise e
    return rids, vectors


def insert_experiment_result(experiment_id: int,
                             experiment_results: str,
                             *,
                             update: bool = True) -> object:
    with DBConnection.getInstance().cursor() as cursor:
        if update:
            query = f'INSERT INTO experiment_results (results, experiment_id, record_id) \
                     VALUES %s \
                     ON CONFLICT (experiment_id, record_id) \
                     DO UPDATE SET (results, experiment_id, record_id )= \
                     (excluded.results::jsonb, \
                     excluded.experiment_id, \
                     excluded.record_id);'
            execute_values(cursor,
                           query,
                           ((json.dumps(v),
                             k) for k, v in experiment_results),
                           template=f"(%s, {experiment_id}, %s)",
                           page_size=100)
        else:
            values = [cursor.mogrify("(%s,%s,%s)", (json.dumps(v), experiment_id, k)
                                     ).decode("utf-8") for k, v in experiment_results]
            values = ','.join(values)
            cursor.execute(f"INSERT INTO experiment_results (results, experiment_id, record_id) VALUES {values} ;")


def get_exp_ids() -> dict:
    # To be replaced then by the fetch from DB/API....
    # Another parameter must be added to specify which 'content' to be rendered(orig, traduction...)
    query = "SELECT expr.id, expr.name, tl.name, tool_id \
             FROM experiments expr \
             INNER JOIN tools tl on tl.id=expr.tool_id"
    with DBConnection.getInstance().cursor() as cursor:
        cursor.execute(query)
        models = {}
        for val in cursor:
            models[val[2]] = models.get(val[2], {})
            models[val[2]].update(**{val[1]: dict(tool_id=val[3],
                                                  experiment_id=val[0])})
    return models


def insert_grpa_ua(ua: dict) -> object:
    with DBConnection.getInstance().cursor() as cursor:
        values = [cursor.mogrify("(%s,%s,%s,%s,%s,%s,%s,%s)",
                                 (v['tstamp'],
                                  v['acttype'],
                                  v['fre'],
                                  v['crsuri'],
                                  v['mdlmoduri'],
                                  json.dumps(v['actiondata']),
                                  json.dumps(v['crsdata']),
                                  json.dumps(v['mdlmoddata']))
                                 ).decode("utf-8") for k, v in enumerate(ua)]
        values = ','.join(values)
        cursor.execute(f"INSERT INTO grpa_user_activities (tstamp, acttype, fre, crsuri, mdlmoduri, actdata, crsdata, mdlmoddata) VALUES {values} ;")


def get_grpa_fredata_x5disc(freobj: dict):
    query = f"SELECT count(grpa.fre) cn, grpa.actdata#>'{{actdata,x5dq}}' x5discq, string_agg(grpa.actdata->>'timestamp', ',') x5discqtsp \
             FROM grpa_user_activities grpa \
             WHERE grpa.fre LIKE '{freobj['fre']}' AND grpa.{freobj['grpgcrta']['name']} LIKE '{freobj['grpgcrta']['value']}' AND grpa.actdata#>'{{actdata,x5dq}}' IS NOT NULL \
             GROUP BY grpa.actdata#>'{{actdata,x5dq}}' \
             ORDER BY cn DESC \
             LIMIT {freobj['max_pdres']} ;"
    with DBConnection.getInstance().cursor() as cursor:
        cursor.execute(query)
        pdres = []
        for val in cursor:
            if val[1] not in [None, 'null', '', ' ']:
                pdres.append({"query": val[1],
                              "nbsearch": val[0],
                              "tspsearch": val[2]})
    return pdres


def get_grpa_fredata_x5rec(freobj: dict, spec_res: List = []):
    query = f"SELECT count(grpa.fre) cn, grpa.actdata#>'{{actdata,x5oerid}}' x5recoer, string_agg(grpa.actdata->>'timestamp', ',') x5oeracstsp \
             FROM grpa_user_activities grpa \
             WHERE grpa.fre LIKE '{freobj['fre']}' AND grpa.{freobj['grpgcrta']['name']} LIKE '{freobj['grpgcrta']['value']}' \
             {get_oers_sql_string(spec_res)} \
             GROUP BY grpa.actdata#>'{{actdata,x5oerid}}' \
             ORDER BY cn DESC ;"
             # LIMIT {freobj['max_pdres']} ;"
    with DBConnection.getInstance().cursor() as cursor:
        cursor.execute(query)
        pdres = {}
        for val in cursor:
            pdres[val[1]] = {"oerid": val[1],
                             "nbacess": val[0],
                             "tspacess": val[2]}
    return pdres


def get_grpa_oeracsdata(freobj: dict, spec_res: List = [], spec_fres: List = []):
    query = f"SELECT count(grpa.fre) cn, grpa.actdata#>'{{actdata,x5oerid}}' x5recoer, string_agg(grpa.actdata->>'timestamp', ',') x5oeracstsp \
             FROM grpa_user_activities grpa \
             WHERE grpa.acttype LIKE 'access' \
             AND grpa.fre IN {get_fres_sql_string(freobj['fre'], spec_fres)} \
             AND grpa.{freobj['grpgcrta']['name']} LIKE '{freobj['grpgcrta']['value']}' \
             {get_oers_sql_string(spec_res)} \
             GROUP BY grpa.actdata#>'{{actdata,x5oerid}}' \
             ORDER BY cn DESC ;"
             # LIMIT {freobj['max_pdres']} ;"
    with DBConnection.getInstance().cursor() as cursor:
        cursor.execute(query)
        pdres = {}
        for val in cursor:
            pdres[val[1]] = {"oerid": val[1],
                             "nbacess": val[0],
                             "tspacess": val[2]}
    return pdres


def get_fres_sql_string(fre_orig, spec_fres):
    sql_str = ''
    if len(spec_fres) > 0:
        sql_str = "(" + ", ".join(list(map(lambda x: "'"+str(x)+"'", spec_fres))) + ")"
    else:
        sql_str = "'"+fre_orig+"'"
    return sql_str


def get_oers_sql_string(oers):
    sql_str = ''
    if len(oers) > 0:
        sql_str = " AND grpa.actdata#>'{{actdata,x5oerid}}' IN (" + ", ".join(list(map(lambda x: "'"+str(x)+"'", oers))) + ")"
    return sql_str


def get_plgn_instancedata(freobj: dict):
    query = f"SELECT grpains.crntstamp crntstamp, grpains.x5rec->'initstr' initstr, grpains.x5rec->'initlst' initlst, grpains.x5rec->'lastlst' lastlst \
             FROM grpa_mdlplgn_instances grpains \
             WHERE grpains.crsuri LIKE '{freobj['insid_data']['crsurl']}' AND grpains.mdlmoduri LIKE '{freobj['insid_data']['modurl']}' \
             ORDER BY crntstamp DESC \
             LIMIT 1;"
    with DBConnection.getInstance().cursor() as cursor:
        cursor.execute(query)
        pdres = {}
        for val in cursor:
            pdres = {"initstr": val[0],
                     "initlst": val[1],
                     "lastlst": val[2]}
    return pdres


def update_plgn_x5rec(freobj, x5rec, x5reconly=False, x5reclast=[]):
    if x5reconly:
        query = f"UPDATE grpa_mdlplgn_instances \
                  SET x5rec = jsonb_set(x5rec::jsonb, '{{lastlst}}', '{json.dumps(','.join(map(str, x5reclast)))}') \
                  WHERE crsuri LIKE '{freobj['insid_data']['crsurl']}' AND mdlmoduri LIKE '{freobj['insid_data']['modurl']}';";
        with DBConnection.getInstance().cursor() as cursor:
            cursor.execute(query)
    else:
        query = f"INSERT INTO grpa_mdlplgn_instances (grpgcrta, x5rec, crsuri, mdlmoduri) \
                 VALUES %s \
                 ON CONFLICT (crsuri, mdlmoduri) \
                 DO UPDATE SET (grpgcrta, x5rec, crsuri, mdlmoduri )= \
                 (excluded.grpgcrta::jsonb, \
                 excluded.x5rec::jsonb, \
                 excluded.crsuri, \
                 excluded.mdlmoduri);"
        with DBConnection.getInstance().cursor() as cursor:
            execute_values(cursor,
                           query,
                           [(json.dumps(freobj['grpgcrta']), json.dumps(x5rec), freobj['insid_data']['crsurl'], freobj['insid_data']['modurl'])],
                           template=f"(%s, %s, %s, %s)",
                           page_size=100)
