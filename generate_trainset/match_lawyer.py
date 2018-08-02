import regex

extract_lawyer = regex.compile("(?<=(Me|Me\.|(M|m)a(i|î)tre|M°) )"
                               "[A-ZÉÈ]+[\w-']*"
                               "( [A-ZÉÈ\-]+[\w-']*)*",
                               flags=regex.VERSION1)


def get_lawyer_name(text: str) -> list:
    """
    Extract lawyer name from text
    :param text: original paragraph text
    :return: offsets as a list
    """
    return [(t.start(), t.end(), "AVOCAT") for t in extract_lawyer.finditer(text)]

