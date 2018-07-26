import regex
from spacy.gold import biluo_tags_from_offsets

upcase_words = "(\s*[A-Z\-]+\w*)+"
upcase_words_regex = regex.compile(upcase_words, flags=regex.VERSION1)

unknown_type_name = "UNKNOWN"


def get_unknown_words_offsets(text: str, offsets: list) -> list:
    """
    Add unknown upcase words offset to existing ones
    :param text: original text
    :param offsets: known offset
    :return: offsets as a list
    """
    unknown_offsets = get_all_unknown_words_offsets(text=text)
    all_offsets = offsets + unknown_offsets
    return clean_unknown_offsets(offsets=all_offsets)


def get_all_unknown_words_offsets(text: str) -> list:
    """
    Find offsets of all words in upcase.
    :param text: original paragraph text
    :return: offsets as a list
    """
    return [(t.start(), t.end(), unknown_type_name) for t in upcase_words_regex.finditer(text)]


def clean_unknown_offsets(offsets: list) -> list:
    """
    Remove offsets of unknown type span when there is an overlap with a known offset
    :param offsets: cleaned offsets with old known offsets and the new ones
    """
    result = list()
    sorted_offsets = sorted(offsets, key=lambda tup: (tup[0], tup[1]))

    for (index, (start_offset, end_offset, type_name)) in enumerate(sorted_offsets):
        if type_name == unknown_type_name:

            # is first?
            if index > 0:
                previous_start_offset, previous_end_offset, previous_type_name = sorted_offsets[index - 1]
            else:
                previous_start_offset, previous_end_offset, previous_type_name = None, None, None

            # is last?
            if index < len(sorted_offsets) - 1:
                next_start_offset, next_end_offset, next_type_name = sorted_offsets[index + 1]
            else:
                next_start_offset, next_end_offset, next_type_name = None, None, None

            is_start_offset_ok = (((previous_end_offset is not None) and (start_offset > previous_end_offset)) or
                                  (previous_end_offset is None))

            is_end_offset_ok = ((next_start_offset is not None) and
                                (end_offset < next_start_offset) or (next_start_offset is None))

            if is_start_offset_ok and is_end_offset_ok:
                result.append((start_offset, end_offset, type_name))

        else:
            result.append((start_offset, end_offset, type_name))
    return result


def convert_bilou_with_missing_action(doc, offsets) -> list:
    """
    Convert unknown type token to missing value for NER
    Therefore no Loss will be applied to these tokens
    :param doc: text tokenized by Spacy
    :param offsets: original offsets
    :return: list of BILOU types
    """
    result = biluo_tags_from_offsets(doc, offsets)
    return ["-" if unknown_type_name in bilou else bilou for bilou in result]


def tokenize_text(model, text: str, offsets: list) -> tuple:
    doc = model(text)
    bilou_annotations = convert_bilou_with_missing_action(doc, offsets)
    return doc, bilou_annotations


def tokenize_texts(model, texts, offsets):
    docs = list()
    bilou_annotations = list()
    for text, current_offsets in zip(texts, offsets):
        doc, bilou_annotation = tokenize_text(model=model, text=text, offsets=current_offsets)
        docs.append(doc)
        bilou_annotations.append(bilou_annotation)
    return docs, bilou_annotations
