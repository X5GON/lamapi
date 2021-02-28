import os
import pickle
import re
from typing import Text
PathType = str

SPECIAL_TOKENS = [r"\[hesitation\]",
                  r"\<unk\>",
                  r"\~SILENCE\~",
                  r"\~SIL",
                  r"\[UNKNOWN\]",
                  r"\[SILENCE\]",
                  r"\[unknown\]",
                  r"\[HESITATION\]"]

# %%


def save_text(text: Text,
              outpath: PathType
              ) -> None:
    print("Saving")
    if not os.path.exists(outpath):
        os.makedirs(outpath)
    with open(outpath, "wb") as f:
        pickle.dump(text, f)
    print("Saving done")

# %%


def remove_tags(text: Text
                ) -> None:
    # This function removes the tags added by the ASR (Automatic Speech Recognition)
    # system in the videos transcriptions
    # example tags: like "~SILENCE~" etc.
    # Parameter: 'text': a string
    # Return: the string 'text' without the tags
    assert type(text) is str, "text must be of type str"
    text = re.sub(r'\<.*?\>', r' ', text)
    text = re.sub(r'|'.join(SPECIAL_TOKENS), ' ', text)
    text = re.sub(r'\n|\r', r' ', text)
    text = re.sub(r' +', r' ', text)
    text = text.replace('&lt;', '<').replace('&gt;', '>').replace(
        '&quot;', '"').replace('&apos;', "'")
    return text


# %%
def test() -> None:
    path = '/home/victor/Programmation/These/x5gon/x5gon-final-resources/all_real_transcriptions/data/e/e4ws06_maksymovych_icpub/video_01/ndz4t3n4a3r3wadrtdoa3kthtlcm2j7k.flv.en.tx.dfxp'
    with open(path, "r") as f:
        text = "".join(f.readlines())
    text = remove_tags(text)
    print(text)


# %%
def main() -> None:
    import argparse
    argparser = argparse.ArgumentParser()
    argparser.add_argument("text",
                           help="path to the transcripition.")
    argparser.add_argument("-o", "--output",
                           help="path to the output text.",
                           default=None)

    args = argparser.parse_args()
    path = args.text
    outpath = args.output
    with open(path, "r") as f:
        text = "".join(f.readlines())
    text = remove_tags(text)
    if outpath:
        save_text(text, outpath)
    else:
        print(text)


# %%
if __name__ == '__main__':
    main()
