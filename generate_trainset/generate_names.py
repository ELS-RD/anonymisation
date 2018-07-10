import re
from random import randint
import string
import regex

org_types = r"société|" \
            r"association|" \
            r"s(\.|\s)*a(\.|\s)*s(\.|\s)*u(\.|\s)*|" \
            r"e(\.|\s)*u(\.|\s)*rl(\.|\s)*|" \
            r"s(\.|\s)*c(\.|\s)*s|" \
            r"s(\.|\s)*c(\.|\s)*p(\.|\s)*|" \
            r"s(\.|\s)*a(\.|\s)*s|" \
            r"s(\.|\s)*a(\.|\s)*|" \
            r"s(\.|\s)*a(\.|\s)*s(\.|\s)*u(\.|\s)*|" \
            r"s(\.|\s)*a(\.|\s)*r(\.|\s)*l|" \
            r"s(\.|\s)*e(\.|\s)*l(\.|\s)*a(\.|\s)*r(\.|\s)*l(\.|\s)*|" \
            r"s(\.|\s)*c(\.|\s)*i(\.|\s)*|" \
            r"s(\.|\s)*c(\.|\s)*o(\.|\s)*p(\.|\s)*|" \
            r"s(\.|\s)*e(\.|\s)*l(\.|\s)*|" \
            r"s(\.|\s)*c(\.|\s)*a(\.|\s)*|" \
            r"e(\.|\s)*i(\.|\s)*r(\.|\s)*l(\.|\s)*|" \
            r"syndic|" \
            r"syndicat|" \
            r"(e|é)tablissement|" \
            r"mutuelle|" \
            r"caisse"

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


find_corp = regex.compile(r"(((?i)" + org_types + ")\s+"
                                                  "("
                                                  "((?i)"
                                                  "(de |le |la |les |pour |l'|et |en )"
                                                  ")*"
                                                  "(\()?[A-Z][[:alnum:]-'\.\)]+(\s|/|-)*)+"
                                                  ")", flags=regex.VERSION1)


def get_company_names(text: str) -> list:
    return [(t.start(), t.end(), "PARTIE_PM") for t in find_corp.finditer(text)]


def get_list_of_pp(paragraphs: list, offsets: list) -> list:
    extracted_names = [text[start_char: end_char] for (text, (start_char, end_char, type_name)) in
                       zip(paragraphs, offsets) if type_name == "PARTIE_PP"]
    return list(set(extracted_names))


translator = str.maketrans(string.punctuation, ' ' * len(string.punctuation))  # map punctuation to space


def get_extend_extracted_name_pattern(texts: list, offsets: list, type_name_to_keep: str) -> regex.Regex:
    """
    Extend names to include first and last name
    :param type_name_to_keep: filter on type name
    :param texts: original text
    :param offsets: discovered offsets from other methods.
    :return: a Regex pattern
    """
    extracted_names = list()
    for text, current_offsets in zip(texts, offsets):
        for (start, end, type_name) in current_offsets:
            if type_name == type_name_to_keep:
                # avoid parentheses and other regex interpreted characters inside the items
                item = text[start:end].translate(translator)
                extracted_names.append(item)

    extracted_names_pattern = '|'.join(extracted_names)
    return regex.compile("(?<=(M(\.?)|Mme(\.?)|Mlle(\.?)|(M|m)onsieur|(M|m)adame|(M|m)ademoiselle)\s+)"
                         "(([A-Z][[:alnum:]-]+\s*)+(" +
                         extracted_names_pattern + "))", flags=regex.VERSION1)


def get_extended_extracted_name(text: str, pattern: regex.Regex, type_name) -> list:
    """
    Apply the generated regex pattern to current paragraph text
    :param text: current original text
    :param pattern: generated regex from get_extend_extracted_name_pattern
    :param type_name: name of the type to apply to each offset
    :return: offset list
    """
    return [(t.start(), t.end(), type_name) for t in pattern.finditer(text)]


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


extract_judge_pattern = regex.compile("(?<=(?i)m |m. |mme |mme. |monsieur |madame )"
                                      "([[:alnum:]-']+\s*)+"
                                      "(?=(?i), (magistrat|"
                                      "conseiller.+(cour|président|magistrat|chambre)|"
                                      "président.+(cour|magistrat|chambre)))")


def get_judge_name(text: str) -> list:
    """
    Extract judge name from text
    :param text: original paragraph text
    :return: offsets as a list
    """
    return [(t.start(), t.end(), "PRESIDENT") for t in extract_judge_pattern.finditer(text)]


extract_clerk_pattern_1 = regex.compile("(?<=(m|M) |(m|M). |(m|M)me |(m|M)me. |(m|M)onsieur |(m|M)adame | )"
                                        "([A-Z]+[[:alnum:]-']*\s*)+(?=.{0,20}(g|G)(reffier|REFFIER)(e|E)?)",
                                        flags=regex.VERSION1)


extract_clerk_pattern_2 = regex.compile("(?<=(G|g)reffier.{0,50})"
                                        "([A-Z]+[[:alnum:]-']+\s*)+", flags=regex.VERSION1)


def get_clerk_name(text: str) -> list:
    """
    Extract clerk name from text
    :param text: original paragraph text
    :return: offsets as a list
    """
    result1 = [(t.start(), t.end(), "GREFFIER") for t in extract_clerk_pattern_1.finditer(text)]
    result2 = [(t.start(), t.end(), "GREFFIER") for t in extract_clerk_pattern_2.finditer(text)]
    return result1 + result2
