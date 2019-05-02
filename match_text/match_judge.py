import regex

extract_judge_pattern_1 = regex.compile(r"("
                                        r"(?!Madame |Monsieur|M\. |Mme\.|M |Mme|Conseil|Présid|Magistrat|Chambre)"
                                        r"[A-ZÉÈ']+[\w']*"
                                        r")"
                                        r"( (de |d')?[A-ZÉÈ\-']+[\w\-']*)*"
                                        r"(?=, "
                                        r"("
                                        r"(M|m)agistrat|"
                                        r"conseill.{0,30}(cour|président|magistrat|chambre|.{0,5}$|"
                                        r", |application des dispositions)|"
                                        r"président.+(cour|magistrat|chambre)|"
                                        r"président.{0,5}$|"
                                        r"(p|P)remier (p|P)résident|"
                                        r"Conseil.*|"
                                        r"Président.*|"
                                        r"(s|S)ubstitut)"
                                        r")",
                                        flags=regex.VERSION1)

extract_judge_pattern_2 = regex.compile(r"(?<=(?i)"
                                        r"^(magistrat|"
                                        r"conseill\w{1,3}|"
                                        r"président\w{0,3})\s+"
                                        r":.{0,20}"
                                        r")"
                                        r"((?!(?i)madame |monsieur |m. |mme. |m |mme |chambre )"
                                        r"[A-ZÉÈ]+[\w\-']*)"
                                        r"( [A-ZÉÈ\-]+[\w\-']*)*",
                                        flags=regex.VERSION1)


def get_judge_name(text: str) -> list:
    """
    Extract judge name from text
    :param text: original paragraph text
    :return: offsets as a list
    """

    r1 = [(t.start(), t.end(), "JUDGE_CLERK_1") for t in extract_judge_pattern_1.finditer(text)]
    r2 = [(t.start(), t.end(), "JUDGE_CLERK_1") for t in extract_judge_pattern_2.finditer(text)]
    return r1 + r2

