import regex

licence_plate_regex = regex.compile(pattern="(?<!(\d|[A-Z])[[:punct:] ]*)"
                                            "\\b"
                                            "([A-Z][\- \.]*){2}"
                                            "([1-9][\- \.]*){3}"
                                            "([A-Z][\- \.]*){2}"
                                            "\\b"
                                            "(?![[:punct:] ]*(\d|[A-Z]))",
                                    flags=regex.VERSION1)


def get_licence_plate(text: str) -> list:
    """
    Find licence plate number following pattern described in
    https://www.developpez.net/forums/d1308588/php/langage/regex/creer-regex-plaque-d-immatriculation/
    :param text: original text
    :return: list of offsets
    """
    pattern = licence_plate_regex.search(text)
    if pattern is not None:
        return [(pattern.start(), pattern.end(), "LICENCE_PLATE")]
    else:
        return []


# print(get_licence_plate("AA111AA"))
# print(get_licence_plate("AA-111-AA"))
# print(get_licence_plate("AA 111 AA"))
# print(get_licence_plate("1 AA111AA"))
# print(get_licence_plate("AA 111 AA 1"))
