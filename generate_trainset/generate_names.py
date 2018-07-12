import re
import string
from random import randint

import acora
import regex
from acora import AcoraBuilder

org_types = r"société|" \
            r"association|" \
            r"s(\.|\s)*a(\.|\s)*s(\.|\s)*u(\.|\s)*|" \
            r"e(\.|\s)*u(\.|\s)*rl(\.|\s)*|" \
            r"s(\.|\s)*c(\.|\s)*s|" \
            r"s(\.|\s)*n(\.|\s)*c|" \
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
            r"caisse|" \
            r"hôpital"

remove_corp_pattern = re.compile(r"\b(" + org_types + r")\b\s+",
                                 flags=re.IGNORECASE)


def remove_corp(original_text: str) -> str:
    """
    Remove corporation type name
    :param original_text: Name of company included its type
    :return: the cleaned string
    """
    return remove_corp_pattern.sub(repl="", string=original_text).strip()


last_name_pattern = re.compile(r"[A-Z\s]+$")


def get_last_name(original_text: str) -> str:
    """
    Extract last name from a full name
    :param original_text: full name
    :return: family name
    """
    result = last_name_pattern.search(original_text.strip())
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


def get_list_of_partie_pp_from_headers_to_search(current_header: dict) -> acora._cacora.UnicodeAcora:
    """
    Create variations of items to search
    :param current_header: original list from headers
    :return: a matcher of string which ignore case
    """
    matcher = AcoraBuilder("@!#$%")

    for full_content, short_content in zip(
            current_header['defendeur_fullname'] + current_header['demandeur_fullname'],
            current_header['defendeur_hidden'] + current_header['demandeur_hidden']):
        if short_content is not None:
            matcher.add(full_content)
            family_name = get_last_name(full_content)
            if len(family_name) > 0:
                matcher.add(family_name)

    return matcher.build(ignore_case=True)


def get_list_of_partie_pm_from_headers_to_search(current_header: dict) -> acora._cacora.UnicodeAcora:
    """
    Create variations of items to search
    :param current_header: original list from headers
    :return: a matcher of string which ignore case
    """
    matcher = AcoraBuilder("@!#$%")

    for full_content, short_content in zip(
            current_header['defendeur_fullname'] + current_header['demandeur_fullname'],
            current_header['defendeur_hidden'] + current_header['demandeur_hidden']):
        if short_content is None:
            matcher.add(full_content)

    return matcher.build(ignore_case=True)


# TODO AJOUTER DES VARIATIONS SANS LE Me
def get_list_of_lawyers_from_headers_to_search(current_header: dict) -> acora._cacora.UnicodeAcora:
    """
    Create variations of items to search
    :param current_header: original list from headers
    :return: a matcher of string which ignore case
    """
    header_content = current_header['avocat']
    matcher = AcoraBuilder("@!#$%")
    matcher.update(header_content)
    for content in header_content:
        family_name = get_last_name(content)
        if len(family_name) > 0:
            matcher.add(family_name)
    return matcher.build(ignore_case=True)


def get_list_of_president_from_headers_to_search(current_header: dict) -> acora._cacora.UnicodeAcora:
    """
    Create variations of items to search
    :param current_header: original list from headers
    :return: a matcher of string which ignore case
    """
    header_content = current_header['president']
    matcher = AcoraBuilder("@!#$%")
    matcher.update(header_content)
    for content in header_content:
        family_name = get_last_name(content)
        if len(family_name) > 0:
            matcher.add(family_name)
    return matcher.build(ignore_case=True)


def get_list_of_conseiller_from_headers_to_search(current_header: dict) -> acora._cacora.UnicodeAcora:
    """
    Create variations of items to search
    :param current_header: original list from headers
    :return: a matcher of string which ignore case
    """
    header_content = current_header['conseiller']
    matcher = AcoraBuilder("@!#$%")
    matcher.update(header_content)
    for content in header_content:
        family_name = get_last_name(content)
        if len(family_name) > 0:
            matcher.add(family_name)
    return matcher.build(ignore_case=True)


def get_list_of_clerks_from_headers_to_search(current_header: dict) -> acora._cacora.UnicodeAcora:
    """
    Create variations of items to search
    :param current_header: original list from headers
    :return: a matcher of string which ignore case
    """
    header_content = current_header['greffier']
    matcher = AcoraBuilder("@!#$%")
    matcher.update(header_content)
    for content in header_content:
        family_name = get_last_name(content)
        if len(family_name) > 0:
            matcher.add(family_name)
    return matcher.build(ignore_case=True)


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
                         extracted_names_pattern + "))",
                         flags=regex.VERSION1)


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


extract_judge_pattern_1 = regex.compile("(?!Madame |Monsieur |M. |Mme. |M |Mme )"
                                        "([A-Z]+[[:alnum:]-']+\s*|de\s+)+"
                                        "(?=, "
                                        "((M|m)agistrat|"
                                        "conseill.{0,5}(cour|président|magistrat|chambre|.{0,5}$|, )|"
                                        "président.+(cour|magistrat|chambre)|"
                                        "président.{0,5}$|"
                                        "Conseill.*|"
                                        "Président.*|"
                                        "(s|S)ubstitut)"
                                        ")",
                                        flags=regex.VERSION1)

extract_judge_pattern_2 = regex.compile("(?<=(?i)"
                                        "^(magistrat|"
                                        "conseill[[:alnum:]]{1,3}|"
                                        "président[[:alnum:]]{0,3})\s+"
                                        ":.{0,20}"                                        
                                        ")"
                                        "((?!(?i)madame |monsieur |m. |mme. |m |mme )[A-Z]+[[:alnum:]-']*\s*)+",
                                        flags=regex.VERSION1)


def get_judge_name(text: str) -> list:
    """
    Extract judge name from text
    :param text: original paragraph text
    :return: offsets as a list
    """

    r1 = [(t.start(), t.end(), "PRESIDENT") for t in extract_judge_pattern_1.finditer(text)]
    r2 = [(t.start(), t.end(), "PRESIDENT") for t in extract_judge_pattern_2.finditer(text)]
    return r1 + r2


extract_clerk_pattern_1 = regex.compile("(?<=(m|M) |(m|M). |(m|M)me |(m|M)me. |(m|M)onsieur |(m|M)adame | )"
                                        "([A-Z]+[[:alnum:]-']*\s*)+(?=.{0,20}"
                                        "(greffier|Greffier|GREFFIER|greffière|Greffière|GREFFIERE))",
                                        flags=regex.VERSION1)

extract_clerk_pattern_2 = regex.compile("(?<=(Greffi|greffi|GREFFI)[^:]{0,50}:.{0,10})"
                                        "((?!Madame |Monsieur |M. |Mme. |M |Mme )[A-Z][[:alnum:]-']+\s*)+",
                                        flags=regex.VERSION1)


def get_clerk_name(text: str) -> list:
    """
    Extract clerk name from text
    :param text: original paragraph text
    :return: offsets as a list
    """
    result1 = [(t.start(), t.end(), "GREFFIER") for t in extract_clerk_pattern_1.finditer(text)]
    result2 = [(t.start(), t.end(), "GREFFIER") for t in extract_clerk_pattern_2.finditer(text)]
    return result1 + result2


extract_lawyer = regex.compile("(?<=(Me|Me.|Ma(i|î)tre)\s)([A-Z]+[[:alnum:]-']+\s*)+",
                               flags=regex.VERSION1)


def get_lawyer_name(text: str) -> list:
    """
    Extract lawyer name from text
    :param text: original paragraph text
    :return: offsets as a list
    """
    return [(t.start(), t.end(), "AVOCAT") for t in extract_lawyer.finditer(text)]


extract_address_pattern = regex.compile("[\d,\-\s]*"
                                        "((?i)(rue|boulevard|bd.?|av.?|avenue|allée|quai))"
                                        "\s+"
                                        "([A-Z]+[[:alnum:]-\.]*"
                                        "(\s*(de|le|la|les|et))?"
                                        "\s*)+"
                                        "[,\-\s]*\d*\s+"
                                        "([A-Z]+[[:alnum:]-\.]*\s*-?\s*((de|le|la|les|et)\s*)?)*",
                                        flags=regex.VERSION1)


def get_addresses(text: str) -> list:
    """
    Extract addresses from text
    :param text: original paragraph text
    :return: offsets as a list
    """
    return [(t.start(), t.end(), "ADRESSE") for t in extract_address_pattern.finditer(text)]
