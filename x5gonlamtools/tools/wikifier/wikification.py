#!/usr/bin/env python
# coding: utf-8

# # Usefull weblinks
# * [Wikifier Documentation]http://wikifier.org/info.html
# * [Wikifier Online Webservice]http://www.wikifier.org/
# * [Janez Brank, Gregor Leban, Marko Grobelnik. Annotating Documents with
# Relevant Wikipedia Concepts. Proceedings of the Slovenian Conference on Data
# Mining and Data Warehouses (SiKDD 2017), Ljubljana, Slovenia, 9 October 2017]
# http://ailab.ijs.si/dunja/SiKDD2017/Papers/Brank_Wikifier.pdf
import functools
import itertools
import requests
import json
import copy
import urllib.request
import urllib.parse
import multiprocessing
from operator import itemgetter
from typing import Dict, Optional, Text, Any, List, Tuple, Callable
from time import sleep

WikificationType = List[Dict[str, Any]]
WikiConceptType = Dict[str, Any]

__DEFAULT_PROCESSES_SETTINGS = multiprocessing.cpu_count()
__DEFAULT_CHUNKS_SETTINGS = dict(chunk_size=9500, window_seek=100, overlap=0)
__DEFAULT_WIKIFICATION_TYPE = "SIMPLE"
__DEFAULT_LONG_TEXT_METHOD_NAME = "sum_classic_page_rank"
# function use to call the wikifier webservice
#oldkey:cbsrrlwdbrogeqsdvmsgzdrwzanwyj
def __wikifier_default_meta_parameter() -> Dict[str, int]:
    return dict(lang="auto",
                userKey="qzyapsompcpaaphcxlqmfrsivaapsw",
                pageRankSqThreshold="0.8",
                applyPageRankSqThreshold="false",
                nTopDfValuesToIgnore="200",
                nWordsToIgnoreFromList="200",
                wikiDataClasses="true",
                wikiDataClassIds="true",
                support="true",
                ranges="false",
                includeCosines="true",
                maxMentionEntropy="3",
                minLinkFrequency="2",
                maxTargetsPerMention="20"
                )


def _call_wikifier(text: Text,
                   parameters: Optional[Dict[str, int]] = None,
                   url: Optional[str] = None
                   ) -> Dict[str, Any]:
    # Use UTF-8 and %-encoding for non-ASCII characters
    # (e.g. text=Beyonc%C3%A9)
    # text = urllib.parse.quote(text)
    data = __wikifier_default_meta_parameter()
    if parameters:
        data.update(parameters)
    # print(data)
    data["text"] = text
    # print("data=", data)
    if not url:
        url = "http://www.wikifier.org/annotate-article"
    # Call the Wikifier and read the response.*
    wikires = []
    attempt = 0
    while not wikires:
        req = requests.post(url, data=data)
        try:
            wikires = req.json()
        except json.decoder.JSONDecodeError as excep:
            attempt += 1
            print("attempt", attempt, '/5')
            sleep(5)
            if attempt > 5:
                print("N'est pas JSON")
                print(req.text)
                raise excep
    return wikires


# Keep only revelant informations from wikifier results
def _extraxt_concepts_from_wikires(wikires: Dict[str, Any],
                                   *,
                                   coeff: int = 1,
                                   wikification_type,
                                   ) -> WikificationType:
    concepts = {"concepts": []}
    sumpr = sum(list(map(itemgetter("pageRank"), wikires["annotations"])))
    sumcos = sum(list(map(itemgetter("cosine"), wikires["annotations"])))
    try:
        for concept in wikires["annotations"]:
            pr, cs = concept["pageRank"] * coeff, concept["cosine"] * coeff
            cur_concepts = {"title": concept["title"],
                            "url": concept["url"],
                            "pageRank": pr,
                            "cosine": cs,
                            "norm_pageRank": pr / sumpr if sumpr != 0 else 0,
                            "norm_cosine": cs / sumcos if sumpr != 0 else 0,
                            "lang": concept["lang"]}
            if wikification_type == "FULL":
                cur_concepts.update({"support": [{"wFrom": sup["wFrom"],
                                                  "wTo": sup["wTo"]}
                                                 for sup in concept["support"]]})
            if wikification_type != "SIMPLE":
                cur_concepts.update({"wikiDataItemId": concept["wikiDataItemId"] if "wikiDataItemId" in concept else [],
                                     "wikiDataClasses": concept["wikiDataClasses"] if "wikiDataClasses" in concept else [],
                                     "wikiDataClassIds": concept["wikiDataClassIds"] if "wikiDataClassIds" in concept else [],
                                     "dbPediaTypes": concept["dbPediaTypes"] if "dbPediaTypes" in concept else [],
                                     "dbPediaIri": concept["dbPediaIri"] if "dbPediaIri" in concept else []})
            concepts["concepts"].append(cur_concepts)
    except Exception as e:
        print("Concept error:", concept)
        raise(e)
    if wikification_type == "FULL":
        concepts["words"] = wikires["words"]
    return concepts


# Cut the text in chunk of size chunk_size. The window_seek try to find the
# best place to cut arround the end of each chunk. Wikifier allows chunk size
# up to 24500.
# Return a list of triplet (subtext, index of character cut in original text,
# number of words in subtext)
def _get_chunks(text: Text,
                chunk_size: int = __DEFAULT_CHUNKS_SETTINGS["chunk_size"],
                window_seek: int = __DEFAULT_CHUNKS_SETTINGS["window_seek"],
                overlap: int = __DEFAULT_CHUNKS_SETTINGS["overlap"]
                ) -> List[Tuple[Text, int, int]]:
    if len(text) < chunk_size:
        return [(text, len(text), len(text.split()))]
    partition, current = [(None, (0, 0), None)], 0

    def index_best_cut(text: Text, current: int) -> List[Tuple[int, int]]:
        min_bound = current - window_seek if current - window_seek > 0 else 0
        max_bound = current + window_seek if current + window_seek < len(text) else -1
        # print(min_bound, max_bound)
        for i, c in enumerate(text[min_bound:max_bound]):
            for k in ["\n", ".", "!", "?", ":", ";", ",", " "]:
                if c == k:
                    return min_bound + i
        return min_bound

    while current + chunk_size - overlap < len(text):
        current += chunk_size - overlap
        current = index_best_cut(text, current)
        start = max(partition[-1][1][1] - overlap, 0)
        chunk = text[start:current]
        partition.append((chunk, (start, current), len(chunk.split())))
    start = max(current - overlap, 0)
    chunk = text[start:]
    partition.append((chunk, (start, len(text)), len(chunk.split())))
    return partition[1:]


# Below 3 way to compute wikifier on large text :
# Compute the sum of pageRank weighted by chunk size for each concepts returned
# by the wikifier for each chunk, return only concept which in the 0.8 of most
# highest pageRank. As far as i know similar to Erik implementation
def __treat_subtext_classic(subtext: Text,
                            wikification_type: Text
                            ) -> WikificationType:
    wikires = _call_wikifier(subtext[0])
    return _extraxt_concepts_from_wikires(wikires,
                                          coeff=subtext[2],
                                          wikification_type=wikification_type)

def __fusion_chunk_result(lconcepts,
                          *,
                          norm: int = 1,
                          wikification_type: str):
    concepts = {"concepts": {}}
    if wikification_type == "FULL":
        concepts["words"] = []
    for i, l in enumerate(lconcepts):
        if wikification_type == "FULL":
            concepts["words"].append(l["words"])
        for c in l["concepts"]:
            try:
                concepts["concepts"][c["url"]]["cosine"] += c["cosine"]
                concepts["concepts"][c["url"]]["pageRank"] += c["pageRank"]
                concepts["concepts"][c["url"]]["norm_pageRank"] += c["norm_pageRank"]
                concepts["concepts"][c["url"]]["norm_cosine"] += c["norm_cosine"]
                if wikification_type == "FULL":
                    concepts["concepts"][c["url"]]["support"].extend([{"wFrom": sup["wFrom"],
                                                                       "wTo": sup["wTo"],
                                                                       "chunk": i}
                                                                       for sup in c["support"]])
            except KeyError:
                concepts["concepts"][c["url"]] = dict(**c)
                if wikification_type == "FULL":
                    concepts["concepts"][c["url"]]["support"] = [{"wFrom": sup["wFrom"],
                                                                  "wTo": sup["wTo"],
                                                                  "chunk": i}
                                                                  for sup in c["support"]]
    concepts["concepts"] = sorted(concepts["concepts"].values(),
                                  key=itemgetter("pageRank"),
                                  reverse=True)
    if norm != 0:
        for c in concepts["concepts"]:
            c["pageRank"] /= norm
            c["cosine"] /= norm
            c["norm_pageRank"] /= norm
            c["norm_cosine"] /= norm
    return concepts

def __concepts_threshold(concepts):
    cumul = sum([c["pageRank"] for c in concepts["concepts"]])
    threshold = cumul * 0.8
    return threshold


def _sum_classic_page_rank(text: Text,
                           *,
                           subprocess: int = __DEFAULT_PROCESSES_SETTINGS,
                           chunks_settings: Dict[str, int] = __DEFAULT_CHUNKS_SETTINGS,
                           wikification_type: str,
                           ) -> WikificationType:
    partition = _get_chunks(text, **chunks_settings)
    # print(f"Ready for {len(partition)} requests for {len(text)} characters")
    # print([(i, s) for p, i, s in partition])
    # accumulate concepts in each subtext
    _treat_subtext_classic = functools.partial(__treat_subtext_classic,
                                               wikification_type=wikification_type)
    if subprocess > 1:
        with multiprocessing.Pool(processes=min(subprocess,
                                                len(partition))) as pool:
            lconcepts = pool.map(_treat_subtext_classic, partition)
    else:
        lconcepts = map(_treat_subtext_classic, partition)

    concepts = __fusion_chunk_result(lconcepts,
                                     norm=sum(list(zip(*partition))[2]),
                                     wikification_type=wikification_type)
    # compute threshold on pageRank to select only revelant concepts
    # Warning: suboptimal implementation
    threshold = __concepts_threshold(concepts)

    cumul = 0
    # print(partition)
    # with open('wikifier.err', 'w') as the_file:
    # the_file.write(str(partition))
    for ind, c in enumerate(concepts["concepts"]):
        cumul += c["pageRank"]
        if cumul > threshold:
            break
    concepts["concepts"] = concepts["concepts"][:ind + 1]
    return concepts


# Similar as previous, but treat all concepts find by the wikifier not only the
# selected ones. Slower due to need to recall wikifier services one time for
# each concept in order to have all information about it, notably
# wikiDataClasses and dbPediaIri.
def __treat_subtext_sum(subtext: Text,
                        wikification_type: str
                        ) -> WikificationType:
    subtext, _, coeff = subtext

    wikires = _call_wikifier(subtext,
                             parameters={"wikiDataClasses": "false",
                                         "wikiDataClassIds": "false",
                                         "applyPageRankSqThreshold": "false",
                                         "support": "false",
                                         "ranges": "true"})
    # treat all candidate concepts, not only at the successfully selected ones
    concepts = {"concepts": {}}
    for mention in wikires["ranges"]:
        for concept in mention["candidates"]:
            # superfluous verification
            if ('ignoredDueToLowLinkCount' not in concept or not concept['ignoredDueToLowLinkCount'])\
            and ('ignoredDueToWikiDataClass' not in concept or not concept['ignoredDueToWikiDataClass'])\
            and (concept['pageRank'] != -1 and concept['cosine'] != -99):
                if concept["url"] not in concepts["concepts"]:
                    concepts["concepts"][concept["url"]] = {"cosine": concept["cosine"] * coeff,
                                                            "pageRank": concept["pageRank"] * coeff,
                                                            "title": concept["title"],
                                                            "lang": wikires["language"],
                                                            "url": concept["url"]}
                    if wikification_type == "FULL":
                        concepts["concepts"][concept["url"]]["support"] = [{"wFrom": mention["wFrom"],
                                                                            "wTo": mention["wTo"]}]
                elif wikification_type == "FULL":
                    concepts["concepts"][concept["url"]]["support"].append({"wFrom": mention["wFrom"],
                                                                            "wTo": mention["wTo"]})
    concepts["concepts"] = list(concepts["concepts"].values())
    if wikification_type == "FULL":
        concepts["words"] = wikires["words"]
    return concepts


# retrieve all kept concept info via multi-threading requests
def __get_concepts_info(c: WikiConceptType) -> WikiConceptType:
    url = "http://www.wikifier.org/concept-info"
    data = {"title": c["title"], "lang": c["lang"]}
    i, done = 0, False
    while not done:
        try:
            wikires = _call_wikifier(None, parameters=data, url=url)
            done = True
        except urllib.error.HTTPError:
            # Usefull due to botleneck effect in wikifier server
            i += 1
            print("URL error", c['title'], "attempt", i)

    c["wikiDataItemId"] = wikires["wikiDataItemId"] if "wikiDataItemId" in wikires else ''
    c["wikiDataClasses"] = wikires["wikiDataClasses"] if "wikiDataClasses" in wikires else []
    c["wikiDataClassIds"] = wikires["wikiDataClassIds"] if "wikiDataClassIds" in wikires else []
    c["dbPediaTypes"] = wikires["dbPediaTypes"] if "dbPediaTypes" in wikires else []
    c["dbPediaIri"] = wikires["dbPediaIri"] if "dbPediaIri" in wikires else ''
    return c


def _sum_page_rank(text: Text,
                   *,
                   subprocess: int = __DEFAULT_PROCESSES_SETTINGS,
                   chunks_settings: Dict[str, int] = __DEFAULT_CHUNKS_SETTINGS,
                   wikification_type: str
                   ) -> WikificationType:
    partition = _get_chunks(text, **chunks_settings)
    # print(f"Ready for {len(partition)} requests for {len(text)} characters")
    # print([(lc, lw) for _, lc, lw in partition])
    # accumulate concepts in each subtext
    _treat_subtext_sum = functools.partial(__treat_subtext_sum,
                                           wikification_type=wikification_type)
    if subprocess > 1:
        with multiprocessing.Pool(processes=min(subprocess,
                                                len(partition))) as pool:
            lconcepts = pool.map(_treat_subtext_sum, partition)
    else:
        lconcepts = map(_treat_subtext_sum, partition)

    concepts = __fusion_chunk_result(lconcepts,
                                     norm=sum(list(zip(*partition))[2]),
                                     wikification_type=wikification_type)

    # compute threshold on pageRank to select only revelant concepts
    threshold = __concepts_threshold(concepts)

    cumul = 0
    for ind, c in enumerate(concepts["concepts"]):
        cumul += c["pageRank"]
        if cumul > threshold:
            break
    concepts["concepts"] = concepts["concepts"][:ind + 1]

    if wikification_type != "SIMPLE":
        if subprocess > 1:
            with multiprocessing.Pool(processes=min(subprocess,
                                                    len(concepts))) as pool:
                concepts["concepts"] = pool.map(__get_concepts_info, concepts["concepts"])
        else:
            concepts["concepts"] = map(__get_concepts_info, concepts["concepts"])
    concepts["concepts"] = sorted(concepts["concepts"],
                                  key=itemgetter("pageRank"),
                                  reverse=True)
    return concepts


# Similar as previous, but treat all concepts find by the wikifier not only the
# selected ones. Slower due to need to recall wikifier services one time for
# each concept in order to have all information about it, notably
# wikiDataClasses and dbPediaIri.
def __treat_subtext(subtext: Text
                    ) -> List[Text]:
    supports = []

    wikires = _call_wikifier(subtext[0],
                             parameters={"wikiDataClasses": "false",
                                         "wikiDataClassIds": "false",
                                         "includeCosines": "false"})
    for concept in wikires["annotations"]:
        for mention in concept["support"]:
            wFrom, wTo = mention["wFrom"], mention["wTo"]
            mention = " ".join(wikires["words"][wFrom:wTo + 1])
            supports.append(mention)
    return supports


def _recompute_on_anchor_text(text: Text,
                              *,
                              subprocess: int = __DEFAULT_PROCESSES_SETTINGS,
                              chunks_settings: Dict[str, int] = __DEFAULT_CHUNKS_SETTINGS,
                              wikification_type: str
                              ) -> WikificationType:
    partition = _get_chunks(text, **chunks_settings)
#     print(f"Ready for {len(partition)} requests, text length {len(text)}")

    # retrieve mention text for each subtext
    _treat_subtext = functools.partial(__treat_subtext,
                                       wikification_type=wikification_type)
    if subprocess > 1:
        #print("parralellized")
        with multiprocessing.Pool(processes=min(subprocess,
                                                len(partition))) as pool:
            concepts = pool.map(_treat_subtext, partition)
    else:
        supports = map(_treat_subtext, partition)

    supports = sum(supports, [])
    # build the new text by concatenation of retrievied mention in each subtext
    newtext = "\n".join(supports)
    # call results on new built text
    concepts = wikification(newtext,
                            long_text_method_name="sum_classic_page_rank",
                            subprocess=subprocess,
                            wikification_type=wikification_type)

    return concepts


def wikification_filter(input_wikifier: dict,
                        wikification_type_needed: str = "FULL",
                        *,
                        in_place: bool = False,
                        ) -> dict:
        if in_place:
            output_wikifier = input_wikifier
        else:
            output_wikifier = copy.deepcopy(input_wikifier)
        if wikification_type_needed == "CLASSIC":
            return __get_classic_wikifier_object(output_wikifier)
        if wikification_type_needed == "SIMPLE":
            return __get_simple_wikifier_object(output_wikifier)
        else:
            return output_wikifier


def __get_classic_wikifier_object(wikifier_object: dict) -> dict:
        if "words" in wikifier_object: wikifier_object.pop('words')
        for concept in wikifier_object['concepts']:
            if "support" in concept: concept.pop('support')
        return wikifier_object


def __get_simple_wikifier_object(wikifier_object: dict) -> dict:
        if "words" in wikifier_object: wikifier_object.pop('words')
        for concept in wikifier_object['concepts']:
            if 'wikiDataItemId' in concept: concept.pop('wikiDataItemId')
            if 'wikiDataClasses' in concept: concept.pop('wikiDataClasses')
            if 'wikiDataClassIds' in concept: concept.pop('wikiDataClassIds')
            if 'dbPediaTypes' in concept: concept.pop('dbPediaTypes')
            if 'dbPediaIri' in concept: concept.pop('dbPediaIri')
            if 'support' in concept: concept.pop('support')
        return wikifier_object


LONG_TEXT_METHODS = {"sum_classic_page_rank": _sum_classic_page_rank,
                     "recompute_on_anchor_text": _recompute_on_anchor_text,
                     "sum_page_rank": _sum_page_rank}
DATA_RETURN_TYPE = ["SIMPLE", "FULL", "CLASSIC"]

def wikification(text: Text,
                 long_text_method_name: str = __DEFAULT_LONG_TEXT_METHOD_NAME,
                 subprocess: int = __DEFAULT_PROCESSES_SETTINGS,
                 wikification_type = __DEFAULT_WIKIFICATION_TYPE,
                 **kwargs
                 ) -> WikificationType:
    if len(text) < 10000:
        return _extraxt_concepts_from_wikires(_call_wikifier(text, **kwargs),
                                              wikification_type=wikification_type)
    else:
        # print(f"text too long {long_text_method.__name__} method used")
        return LONG_TEXT_METHODS[long_text_method_name](text,
                                                        subprocess=subprocess,
                                                        wikification_type=wikification_type,
                                                        **kwargs)
