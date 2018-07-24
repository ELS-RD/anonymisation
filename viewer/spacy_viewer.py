from spacy import displacy

from ner.model_factory import get_empty_model


def convert_offsets_to_spacy_docs(doc_annotated: list, path_model: str) -> list:
    """
    Convert a list of tuple of string with their offset to Spacy doc with entities ready
    :param doc_annotated: list of tuple (string, array of offsets)
    :param path_model: path to a NER model
    :return: list of spacy doc
    """
    model = get_empty_model(load_labels_for_training=False)
    model = model.from_disk(path_model)
    docs = list()
    for case_id, text, tags in doc_annotated:
        doc = model(text)
        ents = list()
        for (start_offset, end_offset, type_name) in tags['entities']:
            span_doc = doc.char_span(start_offset, end_offset, label=type_name)
            if span_doc is not None:
                ents.append(span_doc)
            else:
                print("Issue in offset", text[start_offset:end_offset], text, sep="|")
        doc.ents = ents
        docs.append(doc)
    return docs


def view_spacy_docs(docs: list):
    """
    Launch a server to View entities
    :param docs: spacy doc with entities ready
    """
    colors = {'PARTIE_PP': '#ff9933',
              'ADRESSE': '#ff99cc',
              'PARTIE_PM': '#00ccff',
              'AVOCAT': '#ccffcc',
              'MAGISTRAT': '#ccccff',
              'GREFFIER': '#ccccff',
              'JURIDICTION': '#ccffff',
              'DATE': '#ccffff'}
    options = {'ents': None, 'colors': colors}
    displacy.serve(docs, style='ent', minify=True, port=5000, options=options)
