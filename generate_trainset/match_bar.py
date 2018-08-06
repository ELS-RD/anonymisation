import regex

barreau_pattern = regex.compile("barreau ((?i)de |d'|du )"
                                "[A-ZÉÈ'\-]+\w*"
                                "( (en |de |et les |du )?[A-Z'\-]+\w*)*",
                                flags=regex.VERSION1)


def get_bar(text: str) -> list:
    """
    Extract offset related to a bar and its city localization
    French bar list: http://www.conferencedesbatonniers.com/barreaux/userslist/7-liste-des-barreaux
    :param text: original text
    :return: offset as a list
    """
    return [(t.start(), t.end(), "BAR_1") for t in barreau_pattern.finditer(text)]
