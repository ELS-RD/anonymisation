import regex

extract_judge_pattern_1 = regex.compile("("
                                        "(?!Madame |Monsieur|M\. |Mme\.|M |Mme|Conseil|Présid|Magistrat|Chambre)"
                                        "[A-ZÉÈ']+[\w']*"
                                        ")"
                                        "( (de |d')?[A-ZÉÈ\-']+[\w\-']*)*"
                                        "(?=, "
                                        "("
                                        "(M|m)agistrat|"
                                        "conseill.{0,30}(cour|président|magistrat|chambre|.{0,5}$|"
                                        ", |application des dispositions)|"
                                        "président.+(cour|magistrat|chambre)|"
                                        "président.{0,5}$|"
                                        "(p|P)remier (p|P)résident|"
                                        "Conseil.*|"
                                        "Président.*|"
                                        "(s|S)ubstitut)"
                                        ")",
                                        flags=regex.VERSION1)

extract_judge_pattern_2 = regex.compile("(?<=(?i)"
                                        "^(magistrat|"
                                        "conseill\w{1,3}|"
                                        "président\w{0,3})\s+"
                                        ":.{0,20}"
                                        ")"
                                        "((?!(?i)madame |monsieur |m. |mme. |m |mme |chambre )"
                                        "[A-ZÉÈ]+[\w\-']*)"
                                        "( [A-ZÉÈ\-]+[\w\-']*)*",
                                        flags=regex.VERSION1)


def get_judge_name(text: str) -> list:
    """
    Extract judge name from text
    :param text: original paragraph text
    :return: offsets as a list
    """

    r1 = [(t.start(), t.end(), "JUDGE_CLERK") for t in extract_judge_pattern_1.finditer(text)]
    r2 = [(t.start(), t.end(), "JUDGE_CLERK") for t in extract_judge_pattern_2.finditer(text)]
    return r1 + r2

