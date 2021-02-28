from components.dataconnection.index import get_searchresults_forlamdash
from services.searchengine.searchv1.v1.core import get_resource_search_v1


# Get searchResult for lamdsh
def get_resource_lamdshsearch(search_infos):
    if search_infos['use_model']:
        knn_search = get_resource_search_v1(text=search_infos['search'], x5gon_format=False, **search_infos)
        search_infos.update(resource_ids=knn_search['neighbors'])
    return [rs for rs in get_searchresults_forlamdash(**search_infos)]
