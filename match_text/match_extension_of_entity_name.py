from match_text_unsafe.match_acora import AcoraMatcher
from misc.extract_first_last_name import get_first_last_name
from modify_text.modify_strings import remove_org_type


def get_all_name_variation(texts: list, offsets: list, threshold_span_size: int) -> list:
    """
    Search for any variation of known entities
    :param texts: original text
    :param offsets: discovered offsets
    :param threshold_span_size: minimum size of a name (first / last) to be added to the list
    :return: discovered offsets
    """
    pp_text_span = list()
    pm_text_span = list()
    for current_offsets, text in zip(offsets, texts):
        for offset in current_offsets:
            start_offset, end_offset, type_name = offset
            text_span = text[start_offset:end_offset].strip()
            if len(text_span) > 0:
                if type_name == "PERS":
                    pp_text_span.append(text_span)
                    first_name, last_name = get_first_last_name(text_span)
                    first_name = first_name.strip()
                    last_name = last_name.strip()

                    if len(first_name) > threshold_span_size:
                        pp_text_span.append(first_name)
                    if len(last_name) > threshold_span_size:
                        pp_text_span.append(last_name)

                if type_name == "ORGANIZATION":
                    pm_text_span.append(text_span)
                    short_org_name = remove_org_type(text_span).strip()
                    if (len(short_org_name) > 0) and (short_org_name != text_span):
                        pm_text_span.append(short_org_name)

    pp_matcher = AcoraMatcher(content=pp_text_span, ignore_case=True)
    pm_matcher = AcoraMatcher(content=pm_text_span, ignore_case=True)

    results = list()

    for text, offset in zip(texts, offsets):
        results.append(pp_matcher.get_matches(text=text, tag="PERS") +
                       pm_matcher.get_matches(text=text, tag="ORGANIZATION") +
                       offset)

    return results

