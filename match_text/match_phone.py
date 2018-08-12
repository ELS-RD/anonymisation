import regex

phone_regex = regex.compile(pattern="(?<!\d[[:punct:] ]*)"
                                    "\\b"
                                    "(\()?0[1-9][\- \(\)\.]*(\d[\- \(\)\.]*){8}"
                                    "\\b"
                                    "(?![[:punct:] ]*\d)",
                            flags=regex.VERSION1)


def get_phone_number(text: str) -> list:
    pattern = phone_regex.search(text)
    if pattern is not None:
        return [(pattern.start(), pattern.end(), "PHONE_NUMBER")]
    else:
        return []


# print(get_phone_number("phone: (06)-42-92 72- 29 "))
#
# print(get_phone_number("phone: (06)-42-92 72- 29 + 12"))
#
# print(get_phone_number("phone: (00)-42-92 72- 29 "))
