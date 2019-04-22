from spacy import displacy
from spacy.tokens.doc import Doc

from ner.model_factory import get_empty_model


def convert_offsets_to_spacy_docs(doc_annotated: list) -> list:
    """
    Convert a list of tuple of string with their offset to Spacy doc with entities ready
    :param doc_annotated: list of tuple (string, array of offsets)
    :return: list of spacy doc
    """
    model = get_empty_model(load_labels_for_training=False)
    docs = list()
    for (index, (case_id, text, tags)) in enumerate(doc_annotated):
        doc: Doc = model.make_doc(text)
        ents = list()
        for (start_offset, end_offset, type_name) in tags:
            span_doc = doc.char_span(start_offset, end_offset, label=type_name)
            if span_doc is not None:
                ents.append(span_doc)
            else:
                print("Issue in offset", "Index: " + str(index), "case: " + case_id,
                      text[start_offset:end_offset], text, sep="|")
        doc.ents = ents
        docs.append(doc)
    return docs


def view_spacy_docs(docs: list, port: int):
    """
    Launch a server to View entities
    :param docs: spacy doc with entities ready
    :param port: port to use to serve the file
    """
    colors = {"PERS": "#ff9933",  # orange
              "PHONE_NUMBER": "#ff9933",
              "LICENCE_PLATE": "#ff9933",
              # "SOCIAL_SECURITY_NUMBER": "#ff9933",
              "ADDRESS": "#ff99cc",  # pink
              "ORGANIZATION": "#00ccff",  # blue
              "LAWYER": "#ccffcc",  # light green
              "JUDGE_CLERK": "#ccccff",  # purple
              "COURT": "#ccffff",  # light blue
              "RG": "#99ff99",  # green
              "DATE": "#ffcc99",  # salmon
              "BAR": "#ffe699",  # light yellow
              "UNKNOWN": "#ff0000"}  # red
    options = {"ents": None, "colors": colors}
    displacy.serve(docs, style="ent", minify=True, port=port, options=options)
