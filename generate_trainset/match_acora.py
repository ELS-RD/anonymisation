import acora
from acora import AcoraBuilder


def get_acora_object(content: list, ignore_case: bool) -> acora._cacora.UnicodeAcora:
    """
    Acora matcher factory
    :param content: a list of items to search
    :param ignore_case: True to match any case
    :return: a built matcher
    """
    builder = AcoraBuilder()
    builder.update(content)
    return builder.build(ignore_case=ignore_case)


def get_matches(matcher: acora._cacora.UnicodeAcora, text: str, tag: str)-> list:
    """
    Apply the matcher and return offsets
    :param matcher: the acora matcher (built)
    :param text: original string where to find the matches
    :param tag: the type of offset
    :return: list of offsets
    """
    # matcher not loaded with any pattern
    if matcher.__sizeof__() == 0:
        return []
    results = matcher.findall(text)
    return [(start_offset, start_offset + len(match_text), tag) for match_text, start_offset in results]
