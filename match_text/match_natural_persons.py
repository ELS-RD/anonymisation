import regex

extract_partie_pp_pattern_1 = regex.compile(r"([A-Z][\w-\.\s]{0,15})+(?=.{0,5}\sné(e)?\s.{0,5}\d+)",
                                            flags=regex.VERSION1)

extract_partie_pp_pattern_2 = regex.compile(r"(?<=((?i)consorts|époux|docteur|dr(\.)?|professeur|prof(\.)?)\s+)"
                                            r"([A-ZÉÈ]+[\w]*(?:\s[A-ZÉÈ]+[\w]*)*)",
                                            flags=regex.VERSION1)

extract_partie_pp_pattern_3 = regex.compile(r"((?!Madame|Mme(\.)?)[A-ZÉÈ]+[\w]*(?:\s[A-ZÉÈ]+[\w]*)*) (épouse|veuve) "
                                            r"([A-ZÉÈ]+[\w]*(?:\s[A-ZÉÈ]+[\w]*)*)",
                                            flags=regex.VERSION1)


def get_partie_pers(text: str) -> list:
    """
    Extract people names from text
    :param text: original paragraph text
    :return: offsets as a list
    """
    result1 = [(t.start(), t.end(), "PERS") for t in extract_partie_pp_pattern_1.finditer(text)]
    result2 = [(t.start(), t.end(), "PERS") for t in extract_partie_pp_pattern_2.finditer(text)]
    result3 = [(t.start(), t.end(), "PERS") for t in extract_partie_pp_pattern_3.finditer(text)]
    return result1 + result2 + result3

