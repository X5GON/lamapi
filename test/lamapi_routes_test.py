import os
import argparse
import requests
import json

SERVICES = {
        "temporal/continuousdoc2vec/fetch": ['resource_ids'],
        "temporal/continuouswikifier/fetch": ['resource_ids'],
        "temporal/continuouswikifier/wikify/res": ['resource_ids'],
        "temporal/continuouswikifier/wikify/text": ['resource_texts'],
        "distance/doc2vec/fetch": ['resource_ids'],
        "distance/doc2vec/knn": ['resource_id','n_neighbors'],
        "distance/text2tfidf/fetch": ['resource_ids'],
        "distance/wikifier/fetch": ['resource_ids'],
        "distance/wikifier/knn": ['resource_id', 'n_neighbors'],
        "difficulty/charpersec/res": ['resource_ids'],
        "difficulty/charpersec/text": ['resource_texts'],
        "difficulty/conpersec/res": ['resource_ids'],
        "difficulty/conpersec/text": ['resource_texts'],
        "difficulty/tfidf2technicity/res": ['resource_ids'],
        "difficulty/tfidf2technicity/text": ['resource_texts'],
        "missingresource/missingresources/predictmissing": ['previous', 'after', 'candidate_ids'],
        "ordonize/continuouswikification2order/reordonize": ['resource_id', 'candidate_ids'],
        "preprocess/res": ['resource_ids'],
        "preprocess/text": ['resource_texts'],
}

HEADERS = {
    'accept': 'application/json',
    'Content-Type': 'application/json',
}

VALUES = dict(resource_ids=[ 39435, 39426, 39425, 38657 ],
              resource_id=65478,
              resource_texts=['Go play away...', 'Go play away...'],
              resource_text='Go play away...',
              previous=11777,
              after=11847,
              candidate_ids=[7188, 7279, 7293, 7518, 7519, 8109, 8385, 11098],
              n_neighbors=1)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("SERVICES", help="List of service to test",
                           nargs='+',
                           choices=SERVICES.keys(),
                           default="ALL")
    argparser.add_argument("--ip", help="Adress to the server", type=str)
    args = vars(argparser.parse_args())


services = {
        "temporal/continuousdoc2vec/fetch":['resource_ids'],
        "temporal/continuouswikifier/fetch":['resource_ids'],
        "temporal/continuouswikifier/wikify/res":['resource_ids'],
        "temporal/continuouswikifier/wikify/text":['resource_texts'],
        "distance/doc2vec/fetch":['resource_ids'],
        "distance/doc2vec/knn":['resource_id','n_neighbors'],
        "distance/text2tfidf/fetch":['resource_ids'],
        "distance/wikifier/fetch":['resource_ids'],
        "distance/wikifier/knn":['resource_id', 'n_neighbors'],
        "difficulty/charpersec/res":['resource_ids'],
        "difficulty/charpersec/text":['resource_texts'],
        "difficulty/conpersec/res":['resource_ids'],
        "difficulty/conpersec/text":['resource_texts'],
        "difficulty/tfidf2technicity/res":['resource_ids'],
        "difficulty/tfidf2technicity/text":['resource_texts'],
        "missingresource/missingresources/predictmissing":['previous', 'after', 'candidates_ids'],
        "ordonize/continuouswikification2order/reordonize":['resource_id', 'candidate_ids'],
        "preprocess/res":['resource_ids'],
        "preprocess/text":['resource_ids']
}

tests = SERVICES.keys() if args["SERVICES"] == "ALL" else args["SERVICES"]

for i, t in enumerate(tests):
    print("Request sending:", t, "...")
    print(SERVICES[t])
    try:
        url = os.path.join(f'http://{args["ip"]}', t)
        response = requests.post(url,
                                 headers=HEADERS,
                                 data=json.dumps({k: VALUES[k] for k in SERVICES[t]}))
        print(response)
        print(response.json())
        print(t, "done")
    except KeyError as e:
        print(e)
    except requests.exceptions.ConnectionError as e:
        print(e)
        print(t, "failled")
    if i + 1  != len(tests):
        inp = input("Press a key to continue or Q to Quit...")
        if inp in ["q", "quit", "Quit", "Q"]:
            break
print("Testing done!")
