import spacy

# Managed type of tokens
token_types = ["PARTIE_PP", "PARTIE_PM", "AVOCAT", "MAGISTRAT", "GREFFIER", "ADRESSE"]


# https://github.com/explosion/spaCy/issues/1032
def prevent_sentence_boundary_detection(doc):
    for token in doc:
        # This will entirely disable spaCy's sentence detection
        token.is_sent_start = False
    return doc


def get_empty_model(load_labels_for_training: bool):
    """
    Generate an empty NER model
    :rtype: object
    """
    # Important to setup the right language because it impacts the tokenizer, sentences split, ...
    nlp = spacy.blank('fr')
    nlp.add_pipe(prevent_sentence_boundary_detection, name='prevent-sbd', first=True)
    ner = nlp.create_pipe('ner')
    # add labels
    if load_labels_for_training:
        for token_type in token_types:
            ner.add_label(token_type)

    nlp.add_pipe(ner, last=True)
    return nlp
