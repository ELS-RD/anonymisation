import regex

phone_regex = regex.compile(pattern="(?<!\d[[:punct:] ]*)"
                                    "\\b"
                                    "(\()?0[1-9][\- \)\.]*"
                                    "(\d\d[\- \(\)\.]*){4}"
                                    "\\b"
                                    "(?![[:punct:] ]*\d)",
                            flags=regex.VERSION1)


def get_phone_number(text: str) -> list:
    """
    Find phone number.
    Pattern catch numbers in one block or separated per block of 2 numbers
    :param text: original text
    :return: list of offsets
    """
    patterns = phone_regex.finditer(text)
    result = list()
    for pattern in patterns:
        if pattern is not None and ("compte" not in text):
            result.append((pattern.start(), pattern.end(), "PHONE_NUMBER"))
    return result


# print(get_phone_number("phone: (06)-42-92 72- 29 et 01 44 23 65 89"))
#
# print(get_phone_number("phone: (06)-42-92 72- 29 + 12"))
#
# print(get_phone_number("phone: (00)-42-92 72- 29 "))
