import string

import regex

translator = str.maketrans(string.punctuation, ' ' * len(string.punctuation))  # map punctuation to space


class ExtendNames:
    pattern_title = None
    pattern_extend_right = None
    type_name = None

    def __init__(self, texts: list, offsets: list, type_name_to_keep: str):
        """
        Extend names to include first and last name when explicitly preceded by Monsieur / Madame
        :param type_name_to_keep: filter on type name
        :param texts: original text
        :param offsets: discovered offsets from other methods.
        :return: a Regex pattern
        """
        self.type_name = type_name_to_keep
        extracted_names = list()
        for text, current_offsets in zip(texts, offsets):
            for (start, end, type_name) in current_offsets:
                if type_name == type_name_to_keep:
                    # avoid parentheses and other regex interpreted characters inside the items
                    item = text[start:end].translate(translator).strip()
                    extracted_names.append(item)

        extracted_names_pattern = '|'.join(extracted_names)
        pattern_title = "(?<=M\. |\\bM\\b |Mme |Mlle |(M|m)onsieur |(M|m)adame |(M|m)ademoiselle )" \
                        "(" \
                        "(" \
                        "(?!\\b(M\.)\\b |\\bM\\b |Mme |Mlle |(M|m)onsieur |(M|m)adame |(M|m)ademoiselle )" \
                        "[A-Z]+[[:alnum:]-]*\s*)*" \
                        "\\b(" + \
                        extracted_names_pattern + \
                        ")\\b" \
                        "(\s+[A-Z]+[[:alnum:]-]*)*" \
                        ")"

        pattern_extend_right = "\\b(" + \
                               extracted_names_pattern + \
                               ")\\b" \
                               "(\s+[A-Z]+[[:alnum:]-]*)+"
        self.pattern_title = regex.compile(pattern_title, flags=regex.VERSION1)
        self.pattern_extend_right = regex.compile(pattern_extend_right, flags=regex.VERSION1)

    def get_extended_names(self, text: str) -> list:
        """
        Apply the generated regex pattern to current paragraph text
        :param text: current original text
        :return: offset list
        """
        result1 = [(t.start(), t.end(), self.type_name) for t in self.pattern_title.finditer(text)]
        result2 = [(t.start(), t.end(), self.type_name) for t in self.pattern_extend_right.finditer(text)]
        result = list(set(result1 + result2))
        result = sorted(result, key=lambda tup: tup[0])
        return result

    @staticmethod
    def get_extended_extracted_name_multiple_texts(texts: list, offsets: list, type_name: str) -> list:
        """
        Extend known names for a list of texts and offsets
        :param texts: list of original texts
        :param offsets: list of original offsets
        :param type_name: filter on the type name to extend
        :return: a list of extended offsets
        """
        pattern = ExtendNames(texts=texts,
                              offsets=offsets,
                              type_name_to_keep=type_name)
        result = list()
        for offset, text in zip(offsets, texts):
            current = pattern.get_extended_names(text=text)
            result.append(current + offset)

        return result
