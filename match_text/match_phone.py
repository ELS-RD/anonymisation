import regex

phone_regex = regex.compile(pattern=r"(?<!\d[[:punct:] ]*)"
                                    r"\b"
                                    r"(\()?0[1-9][\- \)\.]*"
                                    r"(\d\d[\- \(\)\.]*){4}"
                                    r"\b"
                                    r"(?![[:punct:] ]*\d)",
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
