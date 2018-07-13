import string

import acora
import regex
from acora import AcoraBuilder

from generate_trainset.first_name_dictionary import get_matches
from generate_trainset.modify_strings import org_types, get_first_last_name


def get_list_of_partie_pp_from_headers_to_search(current_header: dict) -> acora._cacora.UnicodeAcora:
    """
    Create variations of items to search
    :param current_header: original list from headers
    :return: a matcher of string which ignore case
    """
    # this way of init assure that the matcher doesn't expect binary data
    # this may happen if we load empty arrays through update function for instance
    matcher = AcoraBuilder("@!#$%")

    for full_content, short_content in zip(
            current_header['defendeur_fullname'] + current_header['demandeur_fullname'],
            current_header['defendeur_hidden'] + current_header['demandeur_hidden']):
        if short_content is not None:
            matcher.add(full_content)
            first_name, last_name = get_first_last_name(full_content)
            if len(first_name) > 0:
                matcher.add(first_name)
            if len(last_name) > 0:
                matcher.add(last_name)

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
        first_name, last_name = get_first_last_name(content)
        if len(first_name) > 0:
            matcher.add(first_name)
        if len(last_name) > 0:
            matcher.add(last_name)
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
        first_name, last_name = get_first_last_name(content)
        if len(first_name) > 0:
            matcher.add(first_name)
        if len(last_name) > 0:
            matcher.add(last_name)
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
        first_name, last_name = get_first_last_name(content)
        if len(first_name) > 0:
            matcher.add(first_name)
        if len(last_name) > 0:
            matcher.add(last_name)
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
        first_name, last_name = get_first_last_name(content)
        if len(first_name) > 0:
            matcher.add(first_name)
        if len(last_name) > 0:
            matcher.add(last_name)
    return matcher.build(ignore_case=True)


find_corp = regex.compile(r"(((?i)" + org_types + ")\s+"
                                                  "("
                                                  "((?i)"
                                                  "(de |le |la |les |pour |l'|et |en )"
                                                  ")*"
                                                  "(\()?[A-Z][[:alnum:]-'\.\)]+(\s|/|-)*)+"
                                                  ")", flags=regex.VERSION1)


def get_company_names(text: str) -> list:
    """
    Extract company names from string text
    :param text: original text
    :return: a list of offsets
    """
    return [(t.start(), t.end(), "PARTIE_PM") for t in find_corp.finditer(text)]


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


def get_extended_extracted_name(text: str, pattern: regex.Regex, type_name: str) -> list:
    """
    Apply the generated regex pattern to current paragraph text
    :param text: current original text
    :param pattern: generated regex from get_extend_extracted_name_pattern
    :param type_name: name of the type to apply to each offset
    :return: offset list
    """
    return [(t.start(), t.end(), type_name) for t in pattern.finditer(text)]


def get_extended_extracted_name_multiple_texts(texts: list, offsets: list, type_name: str) -> list:
    pattern_to_apply = get_extend_extracted_name_pattern(texts=texts,
                                                         offsets=offsets,
                                                         type_name_to_keep=type_name)
    result = list()
    for offset, text in zip(offsets, texts):
        current = get_extended_extracted_name(text=text, pattern=pattern_to_apply, type_name=type_name)
        result.append(current + offset)

    return result


extract_judge_pattern_1 = regex.compile("(?!Madame |Monsieur |M. |Mme. |M |Mme )"
                                        "([A-Z]+[[:alnum:]-']+\s*|de\s+)+"
                                        "(?=, "
                                        "((M|m)agistrat|"
                                        "conseill.{0,30}(cour|président|magistrat|chambre|.{0,5}$|, )|"
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
                                        "((?i)(rue|boulevard|bd.?|av.?|avenue|allée|quai|place))"
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


extract_partie_pp_pattern_1 = regex.compile("([A-Z][[:alnum:]-\.\s]{0,15})+(?=.{0,5}\sné(e)?\s.{0,5}\d+)",
                                            flags=regex.VERSION1)

extract_partie_pp_pattern_2 = regex.compile("(?<=((?i)consorts|époux|docteur|dr(\.)?|professeur|prof(\.)?)\s+)"
                                            "([A-Z][[:alnum:]-]*(\s+[A-Z][[:alnum:]-]*)+)",
                                            flags=regex.VERSION1)


def get_partie_pp(text: str) -> list:
    """
    Extract people names from text
    :param text: original paragraph text
    :return: offsets as a list
    """
    result1 = [(t.start(), t.end(), "PARTIE_PP") for t in extract_partie_pp_pattern_1.finditer(text)]
    result2 = [(t.start(), t.end(), "PARTIE_PP") for t in extract_partie_pp_pattern_2.finditer(text)]
    return result1 + result2


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
            text_span = text[start_offset:end_offset]
            if len(text_span) > 0:
                if type_name == "PARTIE_PP":
                    pp_patterns.add(text_span)
                    first_name, last_name = get_first_last_name(text_span)
                    if len(first_name) > threshold_span_size:
                        pp_patterns.add(first_name)
                    if len(last_name) > threshold_span_size:
                        pp_patterns.add(last_name)

                if type_name == "PARTIE_PM":
                    pm_patterns.add(text_span)

    pp_matcher = pp_patterns.build(ignore_case=True)
    pm_matcher = pm_patterns.build(ignore_case=True)

    results = list()

    for text, offset in zip(texts, offsets):
        results.append(get_matches(pp_matcher, text, "PARTIE_PP") +
                       get_matches(pm_matcher, text, "PARTIE_PM") +
                       offset)

    return results
