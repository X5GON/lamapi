from services.distance.wikifier.knn.core import knn_wikifier_text
from services.distance.doc2vec.knn.core import knn_doc2vec_text
from services.distance.text2tfidf.knn.core import knn_tfidf_text
from components.dataconnection.index import get_experimental_metadatas, get_experimental_features
from SETTINGS import EXP_IDS


# Get search results from given a text
def get_resource_search_v1(text, remove_duplicates=True, model_type="wikifier", type='', page=0, x5gon_format=True, **kwargs):
    query = {
                "text": text,
                "type": type,
                "page": page,
                "model_type": model_type
            }
    if model_type == "wikifier":
        knn = knn_wikifier_text(resource_text=text,
                                return_dist=True,
                                remove_duplicates=remove_duplicates,
                                n_neighbors=40)
    elif model_type == "doc2vec":
        knn = knn_doc2vec_text(resource_text=text,
                               return_dist=True,
                               remove_duplicates=remove_duplicates,
                               n_neighbors=40)
    elif model_type == "tfidf":
        knn = knn_tfidf_text(resource_text=text,
                             return_dist=True,
                             remove_duplicates=remove_duplicates,
                             n_neighbors=40)
    if x5gon_format:
        return knn_to_x5gon_outputformat(query=query, knn_neighbors=knn, **kwargs)
    else:
        return knn


def knn_to_x5gon_outputformat(query, knn_neighbors, nb_wikiconcepts=5, return_wikisupport=False, remove_nullurlres=True, **kwargs):
    resources_ids = knn_neighbors['neighbors']
    resources_distances = knn_neighbors['distances']
    neighbors_metadata = get_experimental_metadatas(resource_ids=knn_neighbors['neighbors'])
    neighbors_features = []
    if nb_wikiconcepts > 0:
        if return_wikisupport:
            needed_wiki_expid = EXP_IDS['wikifier']['FULL']['experiment_id']
        else:
            needed_wiki_expid = EXP_IDS['wikifier']['SIMPLE']['experiment_id']
        neighbors_features = get_experimental_features(resource_ids=knn_neighbors['neighbors'], experiment_ids=[needed_wiki_expid])
    rec_materials = {}
    # Intialize to garantee to return all the resources
    idx = 0
    for rid in resources_ids:
        rec_materials[rid] = dict(material_id=rid,
                                  weight=resources_distances[idx],
                                  url='',
                                  title='',
                                  description='',
                                  provider='',
                                  author='',
                                  license='',
                                  language='',
                                  type='',
                                  wikipedia=[])
        idx += 1
    # Get all possible resources metadata
    for res in neighbors_metadata:
        # print(res)
        rid = res["id"]
        if remove_nullurlres and res["url"] is None:
            del rec_materials[rid]
            print("resource removed because of null url:", rid)
            continue
        resource_info = rec_materials.get(rid, {})
        resource_info.update(**dict(material_id=res["id"],
                                    url=res["url"],
                                    title=res["title"],
                                    description=res["description"],
                                    provider=res["provider"],
                                    author=res["authors"],
                                    license=res["license"],
                                    language=res["language"],
                                    type=res["type"],
                                    ))
    # Get wikipedia concepts
    for res in neighbors_features:
        rid = res["id"]
        resource_info = rec_materials.get(rid, {})
        resource_info.update(**dict(wikipedia=[dict(title=sres["title"],
                                                url=sres["url"],
                                                pageRank=sres["pageRank"],
                                                cosine=sres["cosine"],
                                                support=sres["support"] if return_wikisupport else None
                                                ) for sres in sorted(res["result"]['value']["concepts"], key = lambda i: i['pageRank'], reverse=True)[:nb_wikiconcepts]]
                                   ))
    return {
            "query": query,
            "rec_materials": list(rec_materials.values()),
            "metadata": {
                "num_or_materials": len(list(rec_materials.values())),
                "max_pages": 0
            }
    }
