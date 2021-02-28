#!/usr/bin/env python
# coding: utf-8

import functools
import multiprocessing
from typing import Any, Dict, List, Text, Tuple
import copy
from x5gonwp3tools.tools.wikifier.wikification import _get_chunks, wikification, wikification_filter


__DEFAULT_WIKIFICATION_TYPE = "SIMPLE"
ContinuousWikificationType = List[List[Dict[Text, Any]]]
__DEFAULT_PROCESSES_SETTINGS = [multiprocessing.cpu_count(), 1]
__DEFAULT_CHUNKS_SETTINGS = dict(chunk_size=5000,
                                 window_seek=100,
                                 overlap=2500)


def _get_overlap_chunks(text: Text,
                        overlap: int = __DEFAULT_CHUNKS_SETTINGS["overlap"],
                        **kwargs
                        ) -> List[Tuple[Text, int, int]]:
    kwargs["overlap"] = overlap
    return _get_chunks(text, **kwargs)


def continuouswikification_filter(input_continuouswikifier: ContinuousWikificationType,
                                  wikification_type_needed: str = "FULL",
                                  *,
                                  in_place: bool = False,
                                  ) -> dict:
    if in_place:
        output_cwikifier = input_continuouswikifier
    else:
        output_cwikifier = copy.deepcopy(input_continuouswikifier)
    for i, cont_wiki_chunk in enumerate(output_cwikifier):
        output_cwikifier[i] = wikification_filter(cont_wiki_chunk,
                                                  in_place=in_place,
                                                  wikification_type_needed=wikification_type_needed)
    return output_cwikifier


def continuous_wikification(text: Text,
                            subprocess: List[int] = __DEFAULT_PROCESSES_SETTINGS,
                            chunks_settings: Dict[str, int] = __DEFAULT_CHUNKS_SETTINGS,
                            **kwargs
                            ) -> ContinuousWikificationType:
    partition = _get_overlap_chunks(text, **chunks_settings)
    functor = functools.partial(wikification,
                                subprocess=subprocess[1],
                                **kwargs)
    if subprocess[0] > 1:
        with multiprocessing.Pool(processes=min(subprocess[0],
                                                len(partition))) as pool:
            lconcepts = pool.map(functor, (t for t, _, _ in partition))
    else:
        lconcepts = list(map(functor, (t for t, _, _ in partition)))
    return lconcepts
