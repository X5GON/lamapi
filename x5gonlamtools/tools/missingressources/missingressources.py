import multiprocessing
import tqdm
import numpy as np
from functools import partial
from operator import itemgetter
from typing import Dict, Tuple, Any, List, Union

Candidate = Tuple[Any, Dict[Any, float]]


def __apply_threshold(v: Candidate,
                      top_n_rate: float
                      ) -> Candidate:
    return v[0], dict(sorted(v[1].items(),
                             key=lambda x: x[1],
                             reverse=True)[:int(top_n_rate * len(v[1]))])


class SelectorSymDiffInterstects:
    def __init__(self,
                 previous: Candidate,
                 after: Candidate
                 ) -> None:
        self.common = set(previous[1].keys()) & set(after[1].keys())
        self.previous = {c: previous[1][c] for c in previous[1].keys() - self.common}
        self.after = {c: after[1][c] for c in after[1].keys() - self.common}
        # print(len(self.after))
        # print(len(self.previous))
        # print(len(set(self.after.keys()) & set(self.previous.keys())))


class SelectorUnionInterstects:
    def __init__(self,
                 previous: Candidate,
                 after: Candidate
                 ) -> None:
        self.previous = previous[1]
        self.after = after[1]


Selector = Union[SelectorUnionInterstects, SelectorSymDiffInterstects]


def score_baseline(prev_s, after_s, cur_s):
    try:
        pred_score = (prev_s + after_s)/abs(prev_s - after_s) * cur_s
    except ZeroDivisionError:
        pred_score = cur_s
    return pred_score


def score_mean(prev_s, after_s, cur_s):
    return (prev_s + after_s) / 2 * cur_s


def score_max(prev_s, after_s, cur_s):
    return max(prev_s, after_s) * cur_s


def score_min(prev_s, after_s, cur_s):
    return max(prev_s, after_s) * cur_s


__scorer = {"mean": score_mean,
            "max": score_max,
            "min": score_min,
            "baseline": score_baseline}


def __score(selector: Selector,
            cur: Candidate,
            score_function: str,
            weighted: bool
            ) -> Dict[str, Any]:
    score_function = __scorer[score_function]
    curid, cur = cur
    print(f"cur:{cur}")
    intprev = selector.previous.keys() & cur.keys()
    intnext = selector.after.keys() & cur.keys()
    kept_c = intprev & intnext
    print(f"kept_c:{kept_c}")
    r_score, r_wscore, scores = 0, 0, {}
    for c in kept_c:
        prev_s = selector.previous[c]
        after_s = selector.after[c]
        cur_s = cur[c]
        pred_score = score_function(prev_s, after_s, cur_s) if weighted else None
        scores[c] = dict(pred_score=pred_score if weighted else 1,
                         previous_score=prev_s,
                         after_score=after_s,
                         cur_score=cur_s)
        r_score += 1
        if weighted:
            r_wscore += pred_score

    return dict(candidate=curid,
                support=r_score,
                pred_score=r_wscore if weighted else r_score,
                sub_score=list(sorted(scores.items(), key=lambda x: x[1]["pred_score"] if weighted else 1, reverse=True)))


def predict_missing(previous: Candidate,
                    after: Candidate,
                    candidates: Dict[Any, Dict[Any, float]],
                    top_n_rate: float = 1/7,
                    nb_processes: int = 1,
                    selector: Selector = SelectorUnionInterstects,
                    score_function: str = "mean",
                    weighted: bool = False
                    ) -> List[Tuple[Any, Dict[str, Any]]]:
    previous = __apply_threshold(previous, top_n_rate)
    after = __apply_threshold(after, top_n_rate)

    print(f"previous:{previous}")
    print(f"after:{after}")
    selector = selector(previous, after)
    preprocessor = partial(__apply_threshold,
                           top_n_rate=top_n_rate)
    scorer = partial(__score,
                     selector=selector,
                     weighted=weighted,
                     score_function=score_function)

    def functor(x: Candidate
                ) -> Dict[str, Any]:
        return scorer(cur=preprocessor(x))

    if nb_processes > 1:
        with multiprocessing.Pool(processes=nb_processes) as pool:
            scores = pool.map(functor, candidates.items())
    else:
        scores = map(functor, candidates.items())
    scores = sorted(scores, key=itemgetter("pred_score"), reverse=True)
    return list(((s["candidate"], s) for s in scores))


# %%
def Test():
    # %%
    import time

    def __random_data(data_size: int = 100,
                      vector_size: int = 100,
                      concept_size: int = 100000,
                      ) -> Dict[Any, Dict[Any, float]]:
        data = {}
        for i in range(data_size + 2):
            data[i] = dict(zip(np.random.randint(concept_size, size=vector_size),
                               np.random.rand(vector_size)))
        return data

    elapsed_times = []
    for data_size in tqdm.tqdm(range(1000, int(1e5), 1000)):
        data = __random_data(data_size=data_size)
        start = time.time()
        res = predict_missing(data.popitem(), data.popitem(), data)
        end = time.time()
        elapsed_times.append(start - end)

    import matplotlib.pyplot as plt
    plt.plot(list(range(1000, int(1e5), 1000)), elapsed_times)
    plt.show()
    # %%
