import re
from random import randint

import regex

org_types = r"société|" \
            r"association|" \
            r"s(\.)?(\s)?a(\.)?s(\.)?u(\.)?|" \
            r"e(\.)?(\s)?u(\.)?rl(\.)?|" \
            r"s(\.)?(\s)?c(\.)?s|" \
            r"s(\.)?(\s)?c(\.)?p(\.)?|" \
            r"s(\.)?(\s)?a(\.)?s|" \
            r"s(\.)?(\s)?a(\.)?|" \
            r"s(\.)?(\s)?a(\.)?s(\.)?u(\.)?|" \
            r"s(\.)?(\s)?a(\.)?r(\.)?l|" \
            r"s(\.)?(\s)?e(\.)?l(\.)?a(\.)?r(\.)?l(\.)?|" \
            r"s(\.)?(\s)?c(\.)i(\.)|" \
            r"s(\.)?(\s)?c(\.)o(\.)p(\.)|" \
            r"s(\.)?(\s)?e(\.)l(\.)|" \
            r"s(\.)?(\s)?c(\.)a(\.)|" \
            r"e(\.)?(\s)?i(\.)?r(\.)?l(\.)?|" \
            r"syndic|" \
            r"syndicat"

remove_corp_pattern = re.compile(r"\b(" + org_types + r")\b\s+", flags=re.IGNORECASE)


def remove_corp(original_text: str) -> str:
    """
    Remove corporation type name
    :param original_text: Name of company included its type
    :return: the cleaned string
    """
    return remove_corp_pattern.sub(repl="", string=original_text).strip()


family_name_pattern = re.compile(r"[A-Z\s]+$")


def get_family_name(original_text: str) -> str:
    """
    Extract family name from a full name
    :param original_text: full name
    :return: family name
    """
    result = family_name_pattern.search(original_text.strip())
    if result:
        return str(result.group(0)).strip()
    return ""


def get_title_case(original_text: str) -> str:
    """
    Upper case each first letter of a MWE
    :param original_text: original full name
    :return: transformed string
    """
    return ' '.join([word.capitalize() for word in original_text.split(' ')])


def add_tag(l: list, tag: str) -> list:
    """
    Build a tag item tuple
    :param l: list of items
    :param tag: tag to add
    :return: a list of tuples
    """
    return [(tag, item) for item in l]


def get_list_of_items_to_search(current_header: dict) -> list:
    """
    Create variations of items to search
    :param current_header: original list from headers
    :return: expanded list of items
    """
    items_to_search = list()
    for full_content, short_content in zip(
            current_header['defendeur_fullname'] + current_header['demandeur_fullname'],
            current_header['defendeur_hidden'] + current_header['demandeur_hidden']):
        if short_content is None:
            items_to_search.append(("PARTIE_PM", full_content))
            no_corp = remove_corp(full_content)
            if no_corp != full_content:
                items_to_search.append(("PARTIE_PM", no_corp))

        else:
            items_to_search.append(("PARTIE_PP", full_content.upper()))
            items_to_search.append(("PARTIE_PP", full_content))
            items_to_search.append(("PARTIE_PP", full_content.lower()))
            items_to_search.append(("PARTIE_PP", get_title_case(full_content)))
            family_name = get_family_name(full_content)
            items_to_search.append(("PARTIE_PP", family_name.upper()))
            items_to_search.append(("PARTIE_PP", family_name))
            items_to_search.append(("PARTIE_PP", family_name.lower()))
            items_to_search.append(("PARTIE_PP", get_title_case(family_name)))

    items_to_search.extend(add_tag(current_header['avocat'], "AVOCAT"))
    # TODO AJOUTER DES VARIATIONS SANS LE Me
    # TODO AJOUTER VARIATIONS Juste avec le nom de famille (si prenom)
    items_to_search.extend(add_tag(current_header['president'], "PRESIDENT"))
    # TODO AJOUTER VARIATIONS Juste avec le nom de famille (si prenom)
    items_to_search.extend(add_tag(current_header['conseiller'], "CONSEILLER"))
    # TODO AJOUTER VARIATIONS Juste avec le nom de famille (si prenom)
    items_to_search.extend(add_tag(current_header['greffier'], "GREFFIER"))
    # TODO AJOUTER VARIATIONS Juste avec le nom de famille (si prenom)
    return items_to_search


find_corp = regex.compile(r"(((?i)" + org_types + ")\s+([A-Z][[:alnum:]-]+(\s|/|-)*)+)", flags=regex.VERSION1)


def get_company_names(text: str) -> list:
    return [(t.start(), t.end(), "PARTIE_PM") for t in find_corp.finditer(text)]


def get_list_of_pp(paragraphs: list, offsets: list) -> list:
    extracted_names = [text[start_char: end_char] for (text, (start_char, end_char, type_name)) in zip(paragraphs, offsets) if type_name == "PARTIE_PP"]
    return list(set(extracted_names))


def get_extend_extracted_name_pattern(texts: list, offsets: list) -> regex.Regex:
    extracted_names = list()
    for text, current_offsets in zip(texts, offsets):
        for (start, end, _) in current_offsets:
            extracted_names.append(text[start:end])

    extracted_names_pattern = '|'.join(extracted_names)
    return regex.compile("(?<=(M(\.?)|Mme(\.?)|Mlle(\.?)|(M|m)onsieur|(M|m)adame|(M|m)ademoiselle)\s+)"
                         "(([A-Z][[:alnum:]-]+\s*)+(" +
                         extracted_names_pattern + "))", flags=regex.VERSION1)
    # return regex.compile("([A-Z][[:alnum:]-]+\s*)+(" + extracted_names_pattern + ")")


def get_extended_extracted_name(text: str, pattern: regex.Regex) -> list:
    return [(t.start(), t.end(), "PARTIE_PP") for t in pattern.finditer(text)]


def random_case_change(text: str, offsets: list, rate: int) -> str:
    """
    Randomly remove the offset case to make the NER more robust
    :param text: original text
    :param offsets: original offsets
    :param rate: the percentage of offset to change (as integer)
    :return: the updated text
    """
    for offset in offsets:
        if randint(0, 99) <= rate:
            extracted_content = text[offset[0]:offset[1]]
            text = text[:offset[0]] + extracted_content.lower() + text[offset[1]:]
    return text
