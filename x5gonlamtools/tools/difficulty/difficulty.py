import datetime
import numpy as np
from scipy.stats import kurtosis
from typing import Dict, Optional, List, Union


def __wpm() -> Dict[str, int]:
    return dict(Audiobooks=160, Slide=125, Fastest=500, Record=637)


def __ch2min(nb_ch: int,
             avg_ch_by_word: int = 5,
             typ: Union[str, float] = __wpm()["Slide"]
             ) -> datetime.timedelta:
    if typ is str:
        typ = __wpm()["Slide"]
    nb_word = nb_ch / avg_ch_by_word
    return datetime.timedelta(minutes=nb_word / typ)


def wikification2con_per_sec(length: int,
                             # wk: List[Dict[str, int]],
                             len_wk: int,
                             duration: Optional[int] = None,
                             avg_ch_by_word: int = 5,
                             typ: Union[str, float] = __wpm()["Slide"]
                             ) -> int:
    if typ is str:
        typ = __wpm()["Slide"]
    if not duration:
        duration = __ch2min(length, avg_ch_by_word, typ).total_seconds()
    return len_wk / duration


def char_per_sec(length: int,
                 duration: Optional[int] = None,
                 avg_ch_by_word: int = 5,
                 typ: Union[str, float] = __wpm()["Slide"]
                 ) -> float:
    if typ is str:
        typ = __wpm()["Slide"]
    if not duration:
        duration = __ch2min(length, avg_ch_by_word, typ).total_seconds()
    return length/duration


def tfidf2technicity(tfidf: Dict[str, int]) -> float:
    values = np.array(list(tfidf.values()))
    minvalue = min(values)
    maxvalue = max(values)
    if minvalue != maxvalue:
        return kurtosis((values - minvalue)/(maxvalue - minvalue))
    else:
        return 0
