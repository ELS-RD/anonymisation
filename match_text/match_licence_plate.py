import regex

new_licence_plate_regex = regex.compile(pattern="(?<!(\d|[A-Z])[[:punct:] ]*)"
                                                "\\b"
                                                "([A-Z][\- \.]*){2}"
                                                "([1-9][\- \.]*){3}"
                                                "([A-Z][\- \.]*){2}"
                                                "\\b"
                                                "(?![[:punct:] ]*(\d|[A-Z]))",
                                        flags=regex.VERSION1)

old_licence_plate_regex = regex.compile(pattern="(?<!(\d|[A-Z])[[:punct:] ]*)"
                                                "\\b"
                                                "([1-9]{1,4}[\- \.]*)"
                                                "[A-Z]{2,3}[\- \.]*"
                                                "[1-9]{2}"
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
    pattern_new = list(new_licence_plate_regex.finditer(text))
    pattern_old = list(old_licence_plate_regex.finditer(text))
    patterns = pattern_new + pattern_old
    results = list()
    for pattern in patterns:
        results.append((pattern.start(), pattern.end(), "LICENCE_PLATE"))
    return results


# print(get_licence_plate("AA111AA"))
# print(get_licence_plate("AA-111-AA"))
# print(get_licence_plate("AA 111 AA"))
# print(get_licence_plate("1 AA111AA"))
# print(get_licence_plate("AA 111 AA 1"))
#
# print(get_licence_plate("1AA11"))
# print(get_licence_plate("9999 ZZZ 99"))
# print(get_licence_plate("9999 ZZZ 999"))
