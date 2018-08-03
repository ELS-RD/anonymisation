from acora import AcoraBuilder

from generate_trainset.match_acora import get_matches
from generate_trainset.modify_strings import remove_org_type, get_first_last_name


def get_all_name_variation(texts: list, offsets: list, threshold_span_size: int) -> list:
    """
    Search for any variation of known entities
    :param texts: original text
    :param offsets: discovered offsets
    :param threshold_span_size: minimum size of a name (first / last) to be added to the list
    :return: discovered offsets
    """
    pp_patterns = AcoraBuilder("!@#$%%^&*")
    pm_patterns = AcoraBuilder("!@#$%%^&*")
    for current_offsets, text in zip(offsets, texts):
        for offset in current_offsets:
            start_offset, end_offset, type_name = offset
            text_span = text[start_offset:end_offset].strip()
            if len(text_span) > 0:
                if type_name == "PERS":
                    pp_patterns.add(text_span)
                    first_name, last_name = get_first_last_name(text_span)
                    first_name = first_name.strip()
                    last_name = last_name.strip()

                    if len(first_name) > threshold_span_size:
                        pp_patterns.add(first_name)
                    if len(last_name) > threshold_span_size:
                        pp_patterns.add(last_name)

                if type_name == "ORGANIZATION":
                    pm_patterns.add(text_span)
                    short_org_name = remove_org_type(text_span).strip()
                    if (len(short_org_name) > 0) and (short_org_name != text_span):
                        pm_patterns.add(short_org_name)

    pp_matcher = pp_patterns.build(ignore_case=True)
    pm_matcher = pm_patterns.build(ignore_case=True)

    results = list()

    for text, offset in zip(texts, offsets):
        results.append(get_matches(pp_matcher, text, "PERS") +
                       get_matches(pm_matcher, text, "ORGANIZATION") +
                       offset)

    return results

