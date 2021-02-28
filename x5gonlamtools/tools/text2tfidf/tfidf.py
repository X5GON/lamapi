import os
import pickle
import operator

from sklearn.feature_extraction.text import TfidfVectorizer
from typing import Text, List, Dict, Tuple, Any

TfidfResultType = Dict[str, Tuple[List[str], Any]]
# Creating the tfidf
def tfidf_ngrams(texts: List[Text],
                 min_n: int = 1,
                 max_n: int = 2,
                 return_format: str = "matrix",
                 sort_keywords: bool = False,
                 stop_words="english",
                 max_df=0.8,
                 max_features=20000,
                 min_df=1e-6,
                 strip_accents="ascii",
                 analyzer="word",
                 use_idf=True,
                 **kwargs
                 ) -> TfidfResultType:
    print(f"Computing tfidf for [{min_n}-{max_n}]-grams")
    # vect = TfidfVectorizer(ngram_range=(min_n, max_n))
    vect = TfidfVectorizer(ngram_range=(min_n, max_n),
                           stop_words=stop_words,
                           max_df=max_df,
                           max_features=max_features,
                           min_df=min_df,
                           strip_accents=strip_accents,
                           analyzer=analyzer,
                           use_idf=use_idf, **kwargs)
    X, Xname = vect.fit_transform(texts), vect.get_feature_names()
    print(f"{len(Xname)} [{min_n}-{max_n}]-grams computed")
    if return_format == "matrix":
        pass
    elif return_format == "dict":
        X = __matrix2dict(X, Xname, sort_keywords)
    else:
        print("Error bad return_format", return_format)
    return dict(X=X, grams=Xname, model=vect)


def __matrix2dict(X, Xname, sort_keywords):
    nb_texts = X.shape[0]
    Xlist = []
    for i in range(nb_texts):
        mat = X.getrow(i).todok().items()
        rec = {Xname[int(k[1])]: v for k, v in mat}
        if sort_keywords:
            rec = dict(sorted(rec.items(),
                              key=operator.itemgetter(1), reverse=True))
        Xlist.append(rec)
    return Xlist


def tfidf_by_ngrams(texts: List[Text],
                    names: List[Any] = [],
                    min_n: int = 1,
                    max_n: int = 2
                    ) -> Dict[str, TfidfResultType]:
    return {**{f"[{1}-{n}]-grams": tfidf_ngrams(texts, min_n=1, max_n=n) for n in range(1, max_n + 1)}, **dict(names=names)}


def save_model(path: str,
               model: TfidfVectorizer):
    outfolder = os.path.split(path)[0]
    if not os.path.exists(outfolder):
        os.makedirs(outfolder)
    with open(path, "wb") as file:
        pickle.dump(model, file)


def load_model(path: str):
    with open(path, "rb") as file:
        res = pickle.load(file)
    return res


def interpolates(texts: List[Text],
                       model: TfidfVectorizer,
                       return_format: str="matrix",
                       sort_keywords: bool=False
                       ):
    X = model.transform(texts)
    Xname = model.get_feature_names()
    if return_format == "matrix":
        return dict(X=X, Xname=Xname)
    elif return_format == "dict":
        return __matrix2dict(X, Xname, sort_keywords)
