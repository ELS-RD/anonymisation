import regex

from generate_trainset.modify_strings import org_types

find_corp = regex.compile("(((?i)" + org_types + ") "
                                                 "((?i)"
                                                 "(de |le |la |les |pour |l'|et |en |des |d'|au |du )"
                                                 ")*"
                                                 "((\()?[A-ZÉÈ&']+[\w\-'\.\)]*)"
                                                 "( (de |le |la |les |pour |l'|et |en |des |d'|au |du |\(|& |/ ?|\- ?)*"
                                                 "[A-ZÉÈ\-&']+[\w\-'\.\)]*"
                                                 ")*"
                                                 ")", flags=regex.VERSION1)


def get_company_names(text: str) -> list:
    """
    Extract company names from string text
    :param text: original text
    :return: a list of offsets
    """
    return [(t.start(), t.end(), "ORGANIZATION") for t in find_corp.finditer(text)]
