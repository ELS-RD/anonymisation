import regex

un_trent_et_un = ["un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf",
                  "dix", "onze", "douze", "treize", "quatorze", "quinze", "seize", "dix.sept", "dix.huit",
                  "dix.neuf", "vingt", "vingt.et.un", "vingt.deux", "vingt.trois", "vingt.quatre",
                  "vint.cinq", "vingt.six", "vingt.sept", "vingt.huit", "vingt.neuf", "trente", "trente.et.un"]

years = ["mille.neuf.cent.quatre.vingts(.et)?", "deux.mille"]

months = ["janvier", "f.vrier", "mars", "avril", "mai", "juin", "juillet", "ao.t",
          "septembre", "octobre", "novembre", "d.cembre"]


def get_or_regex(original_list: list) -> str:
    """
    Transform a list of string to a [OR] regex
    :param original_list:
    :return: string to insert in a regex
    """
    return '|'.join(original_list)


date_pattern_in_letters = "(" + get_or_regex(un_trent_et_un) + ") (" + get_or_regex(months) + ") (" + \
                          get_or_regex(years) + "." + "(" + get_or_regex(un_trent_et_un) + ")?)"

date_pattern_in_letters_regex = regex.compile(date_pattern_in_letters,
                                              flags=regex.VERSION1 | regex.IGNORECASE)

date_pattern_in_numbers_1 = "[0-3]?\d (" + get_or_regex(months) + ") (19|20|20)?\d{2}"
date_pattern_in_numbers_regex_1 = regex.compile(date_pattern_in_numbers_1,
                                                flags=regex.VERSION1 | regex.IGNORECASE)

date_pattern_in_numbers_regex_2 = regex.compile('(\d{1,2}.?(/|\-).?\d{1,2}.?(/|\-).?\d{2,4})',
                                                flags=regex.VERSION1 | regex.IGNORECASE)


def get_date(text: str) -> list:
    """
    Parse text to retrieve offset mentioning a date
    :param text: original text
    :return: offsets as a list
    """
    r1 = [(t.start(), t.end(), "DATE") for t in date_pattern_in_letters_regex.finditer(text)]
    r2 = [(t.start(), t.end(), "DATE") for t in date_pattern_in_numbers_regex_1.finditer(text)]
    r3 = [(t.start(), t.end(), "DATE") for t in date_pattern_in_numbers_regex_2.finditer(text)]
    return r1 + r2 + r3
