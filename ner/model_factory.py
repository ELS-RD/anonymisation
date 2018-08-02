import spacy

# Managed type of tokens
from spacy.lang.fr import French

token_types = ["PERS", "ORGANIZATION", "LAWYER", "JUDGE_CLERK",
               "ADDRESS", "COURT", "DATE", "RG",
               "BAR", "UNKNOWN"]


def prevent_sentence_boundary_detection(doc):
    """
    Disable the sentence splitting done by Spacy
    More info: https://github.com/explosion/spaCy/issues/1032
    :param doc: a Spacy doc
    :return: a disable sentence splitting Spacy doc
    """
    for token in doc:
        # This will entirely disable spaCy's sentence detection
        token.is_sent_start = False
    return doc


def get_empty_model(load_labels_for_training: bool) -> French:
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
