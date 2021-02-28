import os
import pickle

from gensim.models.phrases import Phraser, Phrases
from gensim.utils import SaveLoad as gensimSaveLoad
from typing import List, Text, Any
PathType = str
# TODO: Search truth typing of phraser
PhraserType = Any
# %%


def train_model(texts: List[Text],
                savedir: PathType) -> None:
    print(f"Trainning of phraser model")
    texts = [t.split() for t in texts]
    phrases = [Phraser(Phrases(texts, min_count=100, delimiter=b'_'))]
    corpus = [phrases[-1][texts]]
    for n in range(3, 7):
        save_phraser(phrases[-1], os.path.join(savedir, f"{n-1}gramsphraser"))
        phrases.append(Phraser(Phrases(corpus[-1], delimiter=b'_')))
        corpus.append(phrases[-1][corpus[-1]])


# %%
def save_phraser(phraser: PhraserType,
                 modelpath: PathType
                 ) -> None:
    print(f"phraser saved at {modelpath}")
    if not os.path.exists(os.path.dirname(modelpath)): os.makedirs(os.path.dirname(modelpath))
    phraser.save(modelpath)


# %%
def load_phraser(modelpath: PathType,
                 n: int
                 ) -> PhraserType:
    modelpath = os.path.join(modelpath, f"{n}gramsphraser")
    phraser = gensimSaveLoad.load(modelpath)
    return phraser


# %%
def text2phrase(text: Text,
                model: List,
                size_limit: int=2
                ) -> Text:
    # https://radimrehurek.com/gensim/models/phrases.html
    # The goal of this class is to cut down memory consumption of Phrases, by
    # discarding model state not strictly needed for the bigram detection task.

    # min_count – Ignore all words and bigrams with total collected count lower than this value.
    # threshold – Represent a score threshold for forming the phrases (higher means fewer phrases).
    #             A phrase of words a followed by b is accepted if the score of the phrase is greater than threshold.
    #             Heavily depends on concrete scoring-function.
    # max_vocab_size – Maximum size (number of tokens) of the vocabulary.
    #                  Used to control pruning of less common words, to keep memory under control.
    #                  The default of 40M needs about 3.6GB of RAM.
    #                  Increase/decrease max_vocab_size depending on how much available memory you have.
    # delimiter – Glue character used to join collocation tokens, should be a byte string (e.g. b’_’).
    # scoring – fucntion use to score each pair of words
    text = text.split()
#     print("Beginning of phrasing phase")
    for n, phraser in zip(range(2, size_limit+1), model):
        text = phraser[text]
#         print(f"{n}-phraser:")
#         print([t for t in text if "_" in t])
#     print(f"Phrase of {n}-grams computed")
    text = " ".join(text)
    return text


# %%
def save_phrased_text(text: Text,
                      outpath: PhraserType
                      ) -> None:
#     print("Saving")
    root, _ = os.path.split(outpath)
    if not os.path.exists(root): os.makedirs(root)
    with open(outpath, "w") as f: f.write(text)
#     print("Saving done")


# %%
def test() -> None:
    # %%
    text = '''The Convention on the Elimination of All Forms of Discrimination
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
    print(text)
    text = text2phrase(text.replace("\n", " \n ").strip(), "./models/all_text_transciption_model_07-12-2018/", 5)
    print(text)
    # %%


# %%
def main() -> None:
    import argparse
    argparser = argparse.ArgumentParser()
    argparser.add_argument("text",
                           help="path to the text to phrase (extract revelants n-grams as word).")
    argparser.add_argument("-p", "--phraser",
                           default="./models/all_text_transciption_model_07-12-2018/",
                           help="phraser used to cumpute phrasification")
    argparser.add_argument("-s", "--phrase_limit",
                           default=5, choices=[2, 3, 4, 5],
                           help="limit size for computed phrase in the text")
    argparser.add_argument("-o", "--output",
                           help="path to the output text.")

    args = argparser.parse_args()
    with open(args.text, "r") as f: text = " \n ".join(f.readlines()).strip()

    text = text2phrase(text, args.phraser, args.size_limit)
    save_phrased_text(text, args.output)


# %%
if __name__ == '__main__':
    main()

# %%
