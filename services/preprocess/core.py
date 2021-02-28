from components.dataconnection.index import get_experimental_contents
from x5gonwp3tools.tools.text2processedtext.text2processedtext import preprocess
from x5gonwp3tools.tools.text2phrase.text2phraser import text2phrase
from x5gonwp3tools.tools.tr2text.tr2text import remove_tags
from x5gonwp3models.modelloader import load_model


# model = [load_model("teanlt2r"), load_model("teanlt3r")]


def __preprocess(text, phrase="x5gon", dfxp2text=False, **kwargs):
    if dfxp2text:
        text = remove_tags(text)
    if phrase and phrase == "x5gon":
        text = text2phrase(text, [load_model("teanlt2r"),
                                  load_model("teanlt3r")])
    if phrase and phrase == "wikipedia":
        text = text2phrase(text, [load_model("teaalt2r"),
                                  load_model("teaalt3r")])
    return preprocess(text, **kwargs)


def preprocess_res(resource_ids, **kwargs):
    recovered = get_experimental_contents(resource_ids,
                                          return_content_raw=True)
    return [{"resource_id": res["id"],
             "value": __preprocess(res["content_raw"], **kwargs)
             } for res in recovered]


def preprocess_text(texts, **kwargs):
    return [{"value": __preprocess(res, **kwargs)
             } for res in texts]
