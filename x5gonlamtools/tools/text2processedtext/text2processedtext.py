import os
import re

import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from typing import Text, List

from utils import deprecated


PathType = str
# Load the spacy english model
nlp = spacy.load("en")
STOP_WORDS.add("-PRON-")
STOP_WORDS.add("~sil")


@deprecated
def remove_stopwords(text: Text
                     ) -> Text:
    # This function removes stopwords from a list of strings
    # Parameter: 'list_of_tokens': a list of strings
    # return: 'list_of_tokens' without the stopwords
    list_of_tokens = re.split(r"\s", text)
    assert type(list_of_tokens) is list, "list_of_tokens must be of type list"
    doc = " ".join([t for t in list_of_tokens if t not in STOP_WORDS])
    return re.sub(r' +', r' ', doc)


@deprecated
def lemmatize(text: Text
              ) -> Text:
    # This function lemmatize a string
    # Parameter: 'text': a string
    # return: 'text' wich words have been lemmatised, so a string of lemmas
    assert type(text) is str, "text must be of type str"
    if nlp.max_length < len(text):
        nlp.max_length = len(text)
    doc = nlp(text)
    return " ".join([word.lemma_ for word in doc])


def preprocess(text: Text,
               remove_pos: List[str] = ['ADP',
                                        'ADV',
                                        'AUX',
                                        'CONJ',
                                        'CCCONJ',
                                        'DET',
                                        'INTJ',
                                        'NUM',
                                        'PART',
                                        'PRON',
                                        'PUNCT',
                                        'SCONJ',
                                        'SYM',
                                        'X'],
               remove_stopwords: bool = True,
               lemmatize: bool = True,
               lowercase: bool = True) -> Text:
    # This function remove stopwords, lemmatize and keep only the Nouns, Verbs and Adjectives from the string 'text'
    # Parameter: 'text': a string
    # return: the string 'text' without stopwords and POS that are not Nouns, Verbs and Adjectives, all words lemmatized.
    # Lemmatize and remove stopwords from a string, an keep only Nouns, Verbs and Adjectives, not the other Part Of Speech.
    assert type(text) is str, "text must be of type str"
    if nlp.max_length < len(text):
        nlp.max_length = len(text)
    doc = nlp(text)

    def __cond(word):
        if remove_stopwords and word.lemma_ in STOP_WORDS:
            return False
        if word.pos_ in remove_pos:
            return False
        # print(word, word.tag_)
        return True

    def __transform(word):
        res = word.lemma_ if lemmatize else word.text
        if lowercase:
            res.lower()
        return res

    return " ".join([__transform(word) for word in doc if __cond(word)])


def save_processed_text(text: Text,
                        outpath: PathType
                        ) -> None:
    # print("Saving")
    root, _ = os.path.split(outpath)
    if not os.path.exists(root): os.makedirs(root)
    with open(outpath, "w") as f: f.write(text)
    # print("Saving done")


def test() -> None:
    # %%
    doc = '''The Convention on the Elimination of All Forms of Discrimination
             against Women (CEDAW), adopted in 1979 by the UN General Assembly,
             is often described as an international bill of rights for women.
             Consisting of a preamble and 30 articles, it defines what
             constitutes discrimination against women and sets up an agenda for
             national action to end such discrimination.
             The Convention defines discrimination against women as "...any
             distinction, exclusion or restriction made on the basis of sex
             which has the effect or purpose of impairing or nullifying the
             recognition, enjoyment or exercise by women, irrespective of their
             marital status, on a basis of equality of men and women, of human
             rights and fundamental freedoms in the political, economic,
             social, cultural, civil or any other field."'''
    print(doc)
    # print("*" * 5, "remove_stop_words", "*" * 5)
    # print(remove_stopwords(doc))
    # print("*" * 5, "lemmatize", "*" * 5)
    # print(lemmatize(doc))
    print("*" * 5, "lemmatize_and_remove_unwanted_POS_and_stopwords", "*" * 5)
    print(preprocess(doc))
    print([(w.lemma_, w.pos_) for w in nlp(doc)[0:10]])


def main() -> None:
    import argparse
    argparser = argparse.ArgumentParser()
    argparser.add_argument("text",
                           help="path to the text to phrase (extract revelants n-grams as word).")
    argparser.add_argument("-o", "--output",
                           help="path to the output text.",
                           default=None)
    args = argparser.parse_args()
    path = args.text
    outpath = args.output
    with open(path, "r") as f:
        doc = "".join(f.readlines())
    doc = preprocess(doc)
    if outpath:
        save_processed_text(doc, outpath)
    else:
        print(doc)


# %%
if __name__ == '__main__':
    main()
