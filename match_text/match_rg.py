import regex

extract_rg_from_case_id_pattern = "(?<=\-)\d*(?=\-jurica$)"
extract_rg_from_case_id_regex = regex.compile(pattern=extract_rg_from_case_id_pattern, flags=regex.VERSION1)


class MatchRg:
    case_id = None
    rg = None
    pattern = None

    def __init__(self, case_id: str):
        self.case_id = case_id
        self.rg = self.get_rg_from_case_id()
        self.pattern = regex.compile(pattern=self.get_search_rg_regex(),
                                     flags=regex.VERSION1)

    def get_rg_from_case_id(self) -> list:
        """
        Retrieve the RG from case id, as formatted by Temis
        :return: RG number as a string
        """
        result = extract_rg_from_case_id_regex.findall(self.case_id)
        assert len(result) == 1
        return result[0]

    def get_search_rg_regex(self) -> str:
        """
        Build a regex pattern to find any mention of the RG number corresponding to the one from the Temis case ID
        :return: the pattern as a string
        """
        pattern = [f"({number}([[:punct:]\s])*)" for number in self.rg[0:len(self.rg) - 1]]
        pattern += self.rg[len(self.rg) - 1]
        pattern = ''.join(pattern)
        pattern = "\\b" + pattern + "\\b"
        return pattern

    def get_rg_offset_from_text(self, text: str) -> list:
        """
        Extract RG number offsets from a text, if any
        :param text: original text
        :return: offsets as a list
        """
        return [(item.start(), item.end(), "RG") for item in self.pattern.finditer(text)]

    def get_rg_offset_from_texts(self, texts: list, offsets: list) -> list:
        """
        Extract RG number offsets from a list of texts
        :param texts: original list of texts
        :param offsets: list of offsets
        :return: offsets as a list of lists (including original offsets)
        """
        return [current_offsets + self.get_rg_offset_from_text(text) for text, current_offsets in zip(texts, offsets)]


extract_rg_from_text_pattern = "(?<=(\\bR[[:punct:]]{0,5}G\\b|((?i)répertoire général))" \
                               "[^\d]{0,20})(\d[[:punct:]]*)+( |$)"
extract_rg_from_text_regex = regex.compile(extract_rg_from_text_pattern, flags=regex.VERSION1)


def get_rg_from_regex(text: str) -> list:
    """
    Extract RG number from text when some pattern is found
    :param text: original text
    :return: offset as a list
    """
    offsets = extract_rg_from_text_regex.search(text)
    if offsets is not None:
        return [(offsets.start(), offsets.end(), "RG")]
    else:
        return list()
