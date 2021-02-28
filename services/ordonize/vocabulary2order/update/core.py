import tqdm
import operator
from components.dataconnection.index import (get_all_resource_ids,
                                             get_experimental_features
                                             )
from x5gonwp3tools.tools.vocabulary2order.vocabulary2order import (__create_dataset,
                                                                   novelty)

lids = list(get_all_resource_ids())
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
lids = lids[:1005]
print(lids)
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
cws = (t["result"]["value"] for t in tqdm.tqdm(get_experimental_features(resource_ids=lids,
                                                                                experiment_ids=[2],
                                                                                order_needed=True),
                                                                         total=len(lids),
                                                                         desc="vocalulary2order done"))

dataset = __create_dataset(cws, 10, novelty, operator.itemgetter("PageRank"))
