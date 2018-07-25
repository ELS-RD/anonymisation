from builtins import float
import regex
from acora import AcoraBuilder

from generate_trainset.match_acora import get_matches
from generate_trainset.modify_strings import org_types, get_first_last_name, remove_org_type

find_corp = regex.compile("(((?i)" + org_types + ")\s+"
                                                 "("
                                                 "((?i)"
                                                 "(de |le |la |les |pour |l'|et |en |des |d'|au |du )"
                                                 ")*"
                                                 "(\()?[A-Z][[:alpha:]-'\.\)]+(\s|/|-|&)*)+"
                                                 ")", flags=regex.VERSION1)


def get_company_names(text: str) -> list:
    """
    Extract company names from string text
    :param text: original text
    :return: a list of offsets
    """
    return [(t.start(), t.end(), "PARTIE_PM") for t in find_corp.finditer(text)]


extract_judge_pattern_1 = regex.compile("(?!Madame |Monsieur |M. |Mme. |M |Mme )"
                                        "((?!Conseil|Présid|Magistrat)[A-Z]+[[:alpha:]-']+\s*|de\s+)+"
                                        "(?=, "
                                        "((M|m)agistrat|"
                                        "conseill.{0,30}(cour|président|magistrat|chambre|.{0,5}$|"
                                        ", |application des dispositions)|"
                                        "président.+(cour|magistrat|chambre)|"
                                        "président.{0,5}$|"
                                        "(p|P)remier (p|P)résident|"
                                        "Conseil.*|"
                                        "Président.*|"
                                        "(s|S)ubstitut)"
                                        ")",
                                        flags=regex.VERSION1)

extract_judge_pattern_2 = regex.compile("(?<=(?i)"
                                        "^(magistrat|"
                                        "conseill[[:alpha:]]{1,3}|"
                                        "président[[:alpha:]]{0,3})\s+"
                                        ":.{0,20}"
                                        ")"
                                        "((?!(?i)madame |monsieur |m. |mme. |m |mme )[A-Z]+[[:alpha:]-']*\s*)+",
                                        flags=regex.VERSION1)


def get_judge_name(text: str) -> list:
    """
    Extract judge name from text
    :param text: original paragraph text
    :return: offsets as a list
    """

    r1 = [(t.start(), t.end(), "MAGISTRAT") for t in extract_judge_pattern_1.finditer(text)]
    r2 = [(t.start(), t.end(), "MAGISTRAT") for t in extract_judge_pattern_2.finditer(text)]
    return r1 + r2


extract_clerk_pattern_1 = regex.compile("(?<=(m|M) |(m|M). |(m|M)me |(m|M)me. |(m|M)onsieur |(m|M)adame | )"
                                        "("
                                        "(?!Conseil|Présid|Magistrat|Mme|M |Madame|Monsieur)"
                                        "[A-Z]+[[:alpha:]-']*\s*)+(?=.{0,20}"
                                        "(greffier|Greffier|GREFFIER|greffière|Greffière|GREFFIERE))",
                                        flags=regex.VERSION1)

extract_clerk_pattern_2 = regex.compile("(?<=(Greffi|greffi|GREFFI)[^:]{0,50}:.{0,10})"
                                        "((?!Madame |Monsieur |M. |Mme. |M |Mme )[A-ZÉÈ]+[\w]*(?:\s[A-ZÉÈ]+[\w]*)*)+",
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


extract_lawyer = regex.compile("(?<=(Me|Me.|(M|m)a(i|î)tre)\s)([A-Z]+[[:alpha:]-']+\s*)+",
                               flags=regex.VERSION1)


def get_lawyer_name(text: str) -> list:
    """
    Extract lawyer name from text
    :param text: original paragraph text
    :return: offsets as a list
    """
    return [(t.start(), t.end(), "AVOCAT") for t in extract_lawyer.finditer(text)]


places_pattern = ("rue|boulevard|bd\.?|av(\.|e)?|avenue|allée|quai|"
                  "(?<!(à la |en lieu et ))place|zi|zone industrielle|route")

extract_address_pattern = regex.compile("([\d][\d,/\-\s]*)?"
                                        "("
                                        "(?i)\\b(" +
                                        places_pattern +
                                        ")\\b"
                                        "(\s(de|d'|du|des))?"
                                        "(\s(l'))?"
                                        ")"
                                        "\s*"
                                        "([A-ZÉÈ]+[[:alnum:]-\.']*"
                                        "(\s*(de|le|la|les|et|d'|du))?"
                                        "\s*)+"
                                        "[,\-\sà]*\d*\s*"
                                        "( BP )?"
                                        "("
                                        "[A-Z]+[[:alnum:]-\.]*\s*-?\s*"
                                        "((de|le|la|les|et|d'|du)\s*)?"
                                        ")*"
                                        "( BP )?"
                                        "( CEDEX )?",
                                        flags=regex.VERSION1)


def get_addresses(text: str) -> list:
    """
    Extract addresses from text
    :param text: original paragraph text
    :return: offsets as a list
    """
    result = [(t.start(), t.end(), "ADRESSE") for t in extract_address_pattern.finditer(text)]
    return result


# contain_place_pattern = regex.compile("\\b(" + places_pattern + ")\\b", flags=regex.VERSION1 | regex.IGNORECASE)
start_with_postal_code = regex.compile("^\s*\d{5} (?!Euro.* |Franc.* |Fr )[A-Z]", flags=regex.VERSION1)


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
                offset_street = (0, len(texts[index - 1]), "ADRESSE")
                copy_offsets[index - 1].append(offset_street)
            if len(copy_offsets[index]) == 0:
                postal_code_city = (0, len(text), "ADRESSE")
                copy_offsets[index].append(postal_code_city)
    # reached when offsets is empty
    return copy_offsets


extract_partie_pp_pattern_1 = regex.compile("([A-Z][[:alpha:]-\.\s]{0,15})+(?=.{0,5}\sné(e)?\s.{0,5}\d+)",
                                            flags=regex.VERSION1)

extract_partie_pp_pattern_2 = regex.compile("(?<=((?i)consorts|époux|docteur|dr(\.)?|professeur|prof(\.)?)\s+)"
                                            "([A-ZÉÈ]+[\w]*(?:\s[A-ZÉÈ]+[\w]*)*)",
                                            flags=regex.VERSION1)

extract_partie_pp_pattern_3 = regex.compile("((?!Madame|Mme(\.)?)[A-ZÉÈ]+[\w]*(?:\s[A-ZÉÈ]+[\w]*)*) (épouse|veuve) "
                                            "([A-ZÉÈ]+[\w]*(?:\s[A-ZÉÈ]+[\w]*)*)",
                                            flags=regex.VERSION1)


def get_partie_pp(text: str) -> list:
    """
    Extract people names from text
    :param text: original paragraph text
    :return: offsets as a list
    """
    result1 = [(t.start(), t.end(), "PARTIE_PP") for t in extract_partie_pp_pattern_1.finditer(text)]
    result2 = [(t.start(), t.end(), "PARTIE_PP") for t in extract_partie_pp_pattern_2.finditer(text)]
    result3 = [(t.start(), t.end(), "PARTIE_PP") for t in extract_partie_pp_pattern_3.finditer(text)]
    return result1 + result2 + result3


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
                if type_name == "PARTIE_PP":
                    pp_patterns.add(text_span)
                    first_name, last_name = get_first_last_name(text_span)
                    first_name = first_name.strip()
                    last_name = last_name.strip()

                    if len(first_name) > threshold_span_size:
                        pp_patterns.add(first_name)
                    if len(last_name) > threshold_span_size:
                        pp_patterns.add(last_name)

                if type_name == "PARTIE_PM":
                    pm_patterns.add(text_span)
                    short_org_name = remove_org_type(text_span).strip()
                    if (len(short_org_name) > 0) and (short_org_name != text_span):
                        pm_patterns.add(short_org_name)

    pp_matcher = pp_patterns.build(ignore_case=True)
    pm_matcher = pm_patterns.build(ignore_case=True)

    results = list()

    for text, offset in zip(texts, offsets):
        results.append(get_matches(pp_matcher, text, "PARTIE_PP") +
                       get_matches(pm_matcher, text, "PARTIE_PM") +
                       offset)

    return results


# List of French courts: http://www.justice.gouv.fr/organisation-de-la-justice-10031/lordre-judiciaire-10033/
juridiction_pattern_1 = regex.compile("((?i)Tribunal de grande instance|Tribunal d'instance|Conseil de prud\.*hommes|"
                                      "Tribunal de commerce|Tribunal des affaires de sécurité sociale|"
                                      "Tribunal paritaire des baux ruraux|Cour d'assises|Tribunal correctionnel|"
                                      "Tribunal de police|Juge de proximit.|Juge des enfants|Tribunal pour enfants|"
                                      "Cour d'assises des mineurs|Cour d'appel|"
                                      "Tribunal administratif|Cour administrative d'appel|"
                                      "Cour nationale du droit d'asile|"
                                      "\\bT(\.| )*G(\.| )*I(\.| )*|T(\.| )*I(\.| )*\\b|"
                                      "\\bT(\.| )*A(\.| )*S(\.| )*S(\.| )*\\b)"
                                      "[^A-Z]{0,5}"
                                      "("
                                      "(?!\\bDU\\b\s)"
                                      "[A-Z][A-Z[:alpha:]-']*\s*"
                                      "((de|d'|en)\s*)?"
                                      ")+"
                                      "(?!(?i)\\b(en|le|du)\\b)",
                                      flags=regex.VERSION1)

# http://fr.jurispedia.org/index.php/Liste_des_juridictions_(fr)
juridiction_pattern_2 = regex.compile("Cour de cassation|Conseil d'.tat|INPI|Conseil des prises maritimes|"
                                      "Commission des recours des r.fugi.s|Commissions d.partementales d'aide sociale|"
                                      "Commision d'indemnisation des rapatri.s|Conseil sup.rieur de la magistrature|"
                                      "Tribunal des conflits|Haute cour de justice|Cour de justice de la R.publique|"
                                      "Conseil constitutionnel",
                                      flags=regex.VERSION1 | regex.IGNORECASE)


def get_juridictions(text: str) -> list:
    """
    Extract Courts name from text
    :param text: original paragraph text
    :return: offsets as a list
    """
    result1 = [(t.start(), t.end(), "JURIDICTION") for t in juridiction_pattern_1.finditer(text)]
    result2 = [(t.start(), t.end(), "JURIDICTION") for t in juridiction_pattern_2.finditer(text)]
    return result1 + result2


barreau_pattern = regex.compile("barreau (de |d'|du )(\s*[A-Z\-]+\w*)*",
                                flags=regex.VERSION1)


def get_barreau(text: str) -> list:
    """
    Extract offset related to a bar and its city localization
    :param text: original text
    :return: offset as a list
    """
    return [(t.start(), t.end(), "JURIDICTION") for t in barreau_pattern.finditer(text)]
