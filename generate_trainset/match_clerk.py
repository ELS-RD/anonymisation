import regex

extract_clerk_pattern_1 = regex.compile("(?<=(m|M) |(m|M). |(m|M)me |(m|M)me. |(m|M)onsieur |(m|M)adame | )"
                                        "("
                                        "(?!Conseil|Présid|Magistrat|Mme|M |Madame|Monsieur)"
                                        "[A-ZÉÈ]+[\w-']*\s*)+(?=.{0,20}"
                                        "(greffier|Greffier|GREFFIER|greffière|Greffière|GREFFIERE))",
                                        flags=regex.VERSION1)

extract_clerk_pattern_2 = regex.compile("(?<=(Greffi|greffi|GREFFI)[^:]{0,50}:.{0,10})"
                                        "((?!Madame |Monsieur |M. |Mme. |M |Mme )[A-ZÉÈ]+[\w]*(?:\s[A-ZÉÈ]+[\w]*)*)+",
                                        flags=regex.VERSION1)


def get_clerk_name(text: str) -> list:
    """
    Extract clerk name from text
    :param text: original paragraph text
    :return: offsets as a list
    """
    result1 = [(t.start(), t.end(), "JUDGE_CLERK_1") for t in extract_clerk_pattern_1.finditer(text)]
    result2 = [(t.start(), t.end(), "JUDGE_CLERK_1") for t in extract_clerk_pattern_2.finditer(text)]
    return result1 + result2

