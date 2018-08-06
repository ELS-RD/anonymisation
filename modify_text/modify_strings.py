from random import randint
import regex
from match_text_unsafe.match_acora import get_acora_object, get_matches

# some organization prefix patterns
org_types = "société(s)?|" \
            "association|" \
            "s(\.|\s)*a(\.|\s)*s(\.|\s)*u(\.|\s)*|" \
            "e(\.|\s)*u(\.|\s)*r(\.|\s)*l(\.|\s)*|" \
            "e(\.|\s)*i(\.|\s)*r(\.|\s)*l(\.|\s)*|" \
            "e(\.|\s)*a(\.|\s)*r(\.|\s)*l(\.|\s)*|" \
            "s(\.|\s)*c(\.|\s)*s(\.|\s)*|" \
            "s(\.|\s)*n(\.|\s)*c(\.|\s)*|" \
            "s(\.|\s)*e(\.|\s)*m(\.|\s)*|" \
            "s(\.|\s)*c(\.|\s)*p(\.|\s)*|" \
            "s(\.|\s)*a(\.|\s)*s(\.|\s)*|" \
            "s(\.|\s)*a(\.|\s)*|" \
            "s(\.|\s)*a(\.|\s)*s(\.|\s)*u(\.|\s)*|" \
            "s(\.|\s)*a(\.|\s)*r(\.|\s)*l|" \
            "s(\.|\s)*e(\.|\s)*l(\.|\s)*a(\.|\s)*r(\.|\s)*l(\.|\s)*|" \
            "s(\.|\s)*c(\.|\s)*i(\.|\s)*|" \
            "s(\.|\s)*c(\.|\s)*o(\.|\s)*p(\.|\s)*|" \
            "s(\.|\s)*e(\.|\s)*l(\.|\s)*|" \
            "s(\.|\s)*c(\.|\s)*a(\.|\s)*|" \
            "syndic|" \
            "syndicat( des copropriétaires)?|" \
            "(e|é)tablissement|" \
            "mutuelle|" \
            "caisse|" \
            "h.pital|" \
            "clinique|" \
            "banque|" \
            "compagnie( d'assurance)?|" \
            "cabinet"


remove_org_type_pattern = regex.compile("\\b(" + org_types + ")\\b\s+",
                                        flags=regex.VERSION1 | regex.IGNORECASE)


def remove_org_type(original_text: str) -> str:
    """
    Remove corporation type name
    :param original_text: Name of company included its type
    :return: the cleaned string
    """
    return remove_org_type_pattern.sub(repl="", string=original_text).strip()


key_words_matcher = get_acora_object(["Monsieur", "Madame", "Mme",
                                      "monsieur", "madame",
                                      "la société", "Me", "Maitre", "Maître",
                                      "la SARL", "la SAS", "la SASU", "l'EURL",
                                      "la SA", "la SNC", "la SCP", "la SELAS",
                                      "la SCI", "la SELARL"],
                                     ignore_case=False)


def remove_key_words(text: str, offsets: list, rate: int) -> tuple:
    """
    Modify text to remove some key words, making the learning harder and the model more robust.
    :param text: original paragraph as a string
    :param offsets: list of extracted offsets
    :param rate: chance as an integer between 1 and 100 that a key word is removed
    :return: a tuple (new_text, offsets)
    """
    words_to_delete_offsets: list = get_matches(matcher=key_words_matcher,
                                                text=text,
                                                tag="TO_DELETE")

    if (len(words_to_delete_offsets) == 0) or (len(offsets) == 0):
        return text, offsets

    detected_spans = dict()
    for start_offset, end_offset, type_name in offsets:
        span_text = text[start_offset:end_offset]
        if len(span_text) > 0:
            detected_spans[span_text] = type_name

    if len(detected_spans) == 0:
        return text, offsets

    original_content_offsets_matcher = get_acora_object(content=list(detected_spans.keys()),
                                                        ignore_case=False)

    cleaned_text = list()
    start_selection_offset = 0
    for start_offset, end_offset, _ in words_to_delete_offsets:
        if randint(1, 99) < rate:
            # - 1 to remove also the space following the keyword to remove
            cleaned_text.append(text[start_selection_offset:start_offset - 1])
            start_selection_offset = end_offset
        else:
            cleaned_text.append(text[start_selection_offset:end_offset])
            start_selection_offset = end_offset

    cleaned_text.append(text[start_selection_offset:len(text)])

    cleaned_text = ''.join(cleaned_text)

    updated_offsets = get_matches(matcher=original_content_offsets_matcher,
                                  text=cleaned_text,
                                  tag="UNKNOWN")

    offsets_to_return = list()

    # restore original offset type name
    for start_offset, end_offset, _ in updated_offsets:
        span_text = cleaned_text[start_offset:end_offset]
        type_name = detected_spans[span_text]
        offsets_to_return.append((start_offset, end_offset, type_name))

    return cleaned_text, offsets_to_return
