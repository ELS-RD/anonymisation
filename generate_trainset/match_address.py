import regex

places_pattern = ("rue|chemin|boulevard|bd\.?|bld|av(\.|e)?|avenue|allée|quai|"
                  "(?<!(à la |en lieu et ))place|zi|zone industrielle|route")

extract_address_pattern = regex.compile("([\d][\d,/\- ]*)?"
                                        "("
                                        "(?i)\\b(" +
                                        places_pattern +
                                        ")\\b"
                                        "( (de |d'|du |des |l'|le |la )*)?"
                                        ")"
                                        "[A-ZÉÈ\-]+[\w\-\.']*"
                                        "( (de |le |la |les |et |d'|du |l'|à )*[A-ZÉÈ\-]+[\w\-\.']*)*"
                                        "[\- à\d]*"
                                        "("
                                        "\\b[A-ZÉÈ\-]+[\w\-\.']*\\b"
                                        "( (de |le |la |les |et |d'|du |sur )*[A-ZÉÈ\-]+[\w\-\.']*)*"
                                        ")?",
                                        flags=regex.VERSION1)


def get_addresses(text: str) -> list:
    """
    Extract addresses from text
    :param text: original paragraph text
    :return: offsets as a list
    """
    result = [(t.start(), t.end(), "ADDRESS_1") for t in extract_address_pattern.finditer(text)]
    return result


# contain_place_pattern = regex.compile("\\b(" + places_pattern + ")\\b", flags=regex.VERSION1 | regex.IGNORECASE)
start_with_postal_code = regex.compile("^\s*\d{5} (?!Euro.* |Franc.* |Fr )[A-ZÉÈ]", flags=regex.VERSION1)


def find_address_in_block_of_paragraphs(texts: list, offsets: list) -> list:
    """
    Search a multi paragraph pattern of address in the first half of a case:
    - a line mentioning a street
    - followed by a line starting with a postal code
    :param texts: all original paragraph of a case
    :param offsets: all offsets found in a case as a list
    :return: the list of found offsets updated by the new offsets
    """
    limit = int(len(texts) / 2)
    copy_offsets = offsets.copy()
    for (index, (text, current_offsets)) in enumerate(zip(texts, copy_offsets)):
        if index > limit:
            return copy_offsets
        elif (index >= 1) and \
                (len(text) < 100) and \
                (len(texts[index - 1]) < 100) and \
                ((len(copy_offsets[index - 1]) == 0) or (len(copy_offsets[index]) == 0)) and \
                (start_with_postal_code.search(text) is not None):
            # and \
            #     (contain_place_pattern.search(texts[index - 1]) is not None):
            if len(copy_offsets[index - 1]) == 0:
                offset_street = (0, len(texts[index - 1]), ""
                                                           "ADDRESS")
                copy_offsets[index - 1].append(offset_street)
            if len(copy_offsets[index]) == 0:
                postal_code_city = (0, len(text), "ADDRESS")
                copy_offsets[index].append(postal_code_city)
    # reached when offsets is empty
    return copy_offsets
