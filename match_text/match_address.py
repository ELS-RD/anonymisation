import regex

places_pattern = ("rue|chemin|boulevard|bd\.?|bld|av(\.|e)?|avenue|allée|quai|"
                  "(?<!(à la |en lieu et ))place|zi|zone industrielle|route")

extract_address_pattern_1 = regex.compile("([\d][\d,/\- ]*)?"
                                          "("
                                          "(?i)\\b(" +
                                          places_pattern +
                                          ")\\b"
                                          "( (de |d'|du |des |l'|le |la )*)?"
                                          ")"
                                          "[A-ZÉÈ\-]+[\w\-\.']*"
                                          "( (de |le |la |les |et |d'|du |l'|à |À )*[A-ZÉÈ\-]+[\w\-\.',]*)*"
                                          "[\- àÀ\d]*"
                                          "("
                                          "\\b[A-ZÉÈ\-]+[\w\-\.']*\\b"
                                          "( (de |le |la |les |et |d'|du |sur )*[A-ZÉÈ\-]+[\w\-\.']*)*"
                                          ")?",
                                          flags=regex.VERSION1)

extract_address_pattern_2 = regex.compile("(?<=demeurant [^\dA-Z]{0,25}( )?)(\d|[A-Z]).*\d{5} "
                                          "\\b[A-ZÉÈ\-]+[\w\-\.']*\\b"
                                          "( (de |le |la |les |et |d'|du |sur )*[A-ZÉÈ\-]+[\w\-\.']*)*"
                                          ,
                                          flags=regex.VERSION1)

extract_address_pattern_3 = regex.compile("(?<=cadastré(e)?(s)? ).{1,30}\\d+",
                                          flags=regex.VERSION1)


def get_addresses(text: str) -> list:
    """
    Extract addresses from text
    :param text: original paragraph text
    :return: offsets as a list
    """
    result1 = [(t.start(), t.end(), "ADDRESS_1") for t in extract_address_pattern_1.finditer(text)]
    result2 = [(t.start(), t.end(), "ADDRESS_1") for t in extract_address_pattern_2.finditer(text)]
    result3 = [(t.start(), t.end(), "ADDRESS_1") for t in extract_address_pattern_3.finditer(text)]

    return sorted(list(set(result1 + result2 + result3)), key=lambda tup: (tup[0], tup[1]))


# contain_place_pattern = regex.compile("\\b(" + places_pattern + ")\\b", flags=regex.VERSION1 | regex.IGNORECASE)
start_with_postal_code = regex.compile("^\s*\d{5} (?!Euro.* |Franc.* |Fr )[A-ZÉÈ]", flags=regex.VERSION1)


def get_stripped_offsets(text: str, tag: str) -> tuple:
    """
    Get offsets of a the actual text ie. the text without the surronding whitespaces
    :param text: a line of text
    :param tag: tag to apply to the text
    :return: a tuple (start offset, end offset, tag name)
    """
    stripped_text = text.strip()
    start = text.find(stripped_text)
    end = start + len(stripped_text)
    return (start, end, tag)


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
                offset_street = get_stripped_offsets(texts[index -1], "ADDRESS")
                copy_offsets[index - 1].append(offset_street)
            if len(copy_offsets[index]) == 0:
                postal_code_city = get_stripped_offsets(text, "ADDRESS")
                copy_offsets[index].append(postal_code_city)
    # reached when offsets is empty
    return copy_offsets


clean_address_regex: regex = regex.compile(pattern="^(?i)(demeurant|domicilié(e|s)?( ensemble)?)[^\w]*",
                                           flags=regex.VERSION1)


def clean_address_offset(text: str, offsets: list) -> list:
    """
    Remove some common mentions in addresses which are not related to the address.
    :param text: original text
    :param offsets: list of offsets provided as tuples
    :return: cleaned list of offsets
    """
    result_offsets = list()
    for start, end, type_name in offsets:
        if type_name == "ADDRESS":
            address_span = text[start:end]
            found_text_to_remove = clean_address_regex.search(address_span)
            if found_text_to_remove is not None:
                result_offsets.append((found_text_to_remove.end(), end, type_name))
            else:
                result_offsets.append((start, end, type_name))
        else:
            result_offsets.append((start, end, type_name))
    return result_offsets


def clean_address_offsets(texts: list, offsets: list) -> list:
    result_offsets = list()
    for text, current_offset in zip(texts, offsets):
        cleaned_offsets = clean_address_offset(text=text, offsets=current_offset)
        result_offsets.append(cleaned_offsets)
    return result_offsets
