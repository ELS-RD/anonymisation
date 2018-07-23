import string

import regex

translator = str.maketrans(string.punctuation, ' ' * len(string.punctuation))  # map punctuation to space


class ExtendNames:
    pattern = None

    def __init__(self, texts: list, offsets: list, type_name_to_keep: str):
        """
        Extend names to include first and last name when explicitly preceded by Monsieur / Madame
        :param type_name_to_keep: filter on type name
        :param texts: original text
        :param offsets: discovered offsets from other methods.
        :return: a Regex pattern
        """
        extracted_names = list()
        for text, current_offsets in zip(texts, offsets):
            for (start, end, type_name) in current_offsets:
                if type_name == type_name_to_keep:
                    # avoid parentheses and other regex interpreted characters inside the items
                    item = text[start:end].translate(translator).strip()
                    extracted_names.append(item)

        extracted_names_pattern = '|'.join(extracted_names)
        # "(?!M\.?|Mme|Mlle|(M|m)onsieur|(M|m)adame|(M|m)ademoiselle)" + \
        pattern_string = "(?<=M\. |M |Mme |Mlle |(M|m)onsieur |(M|m)adame |(M|m)ademoiselle )" \
                         "(" \
                         "(" \
                         "(?!M\. |M |Mme |Mlle |(M|m)onsieur |(M|m)adame |(M|m)ademoiselle )" \
                         "[A-Z][[:alnum:]-]+\s*)*" \
                         "(" + \
                         extracted_names_pattern + \
                         ")" \
                         "(\s+[A-Z][[:alnum:]-]+)*" \
                         ")"
        self.pattern = regex.compile(pattern_string, flags=regex.VERSION1)

    def get_extended_names(self, text: str, type_name: str) -> list:
        """
        Apply the generated regex pattern to current paragraph text
        :param text: current original text
        :param type_name: name of the type to apply to each offset
        :return: offset list
        """
        return [(t.start(), t.end(), type_name) for t in self.pattern.finditer(text)]

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
            current = pattern.get_extended_names(text=text, type_name=type_name)
            result.append(current + offset)

        return result
