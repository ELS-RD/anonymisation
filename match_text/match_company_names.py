import regex

from modify_text.modify_strings import org_types

find_corp = regex.compile("(((?i)" + org_types + r") "
                                                 r"((?i)"
                                                 r"(de |le |la |les |pour |l'|et |en |des |d'|au |du )"
                                                 r")*"
                                                 r"((\()?[A-ZÉÈ&']+[\w\-'\.\)]*)"
                                                 r"( (de |le |la |les |pour |l'|et |en |des |d'|au |du |\(|& |/ ?|\- ?)*"
                                                 r"[A-ZÉÈ\-&']+[\w\-'\.\)]*"
                                                 r")*"
                                                 r")", flags=regex.VERSION1)


def get_company_names(text: str) -> list:
    """
    Extract company names from string text
    :param text: original text
    :return: a list of offsets
    """
    return [(t.start(), t.end(), "ORGANIZATION_1") for t in find_corp.finditer(text)]
