import regex

from generate_trainset.match_first_name_dictionary import FirstName


class MatchDoubfulMwe:
    unknown_type_name = "UNKNOWN"
    pattern = "(?!M\. |\\bM\\b |Mme |Mlle |(M|m)onsieur |(M|m)adame |(M|m)ademoiselle )" \
              "[A-ZÉÈ\-]+\w*" \
              "( [A-ZÉÈ\-]+\w*)*"
    upcase_words_regex = regex.compile(pattern=pattern, flags=regex.VERSION1)
    first_name_matcher = FirstName(ignore_case=False)

    def add_unknown_words_offsets(self, texts: list, offsets: list) -> list:
        """
        Add offsets of UNKNOWN words
        :param texts: list of original texts
        :param offsets: list of list of offsets
        :return: list of list of offsets including offset of unknown words
        """
        result = list()
        for text, current_offsets in zip(texts, offsets):
            new_offset = self.get_unknown_words_offsets(text=text, offsets=current_offsets)
            result.append(new_offset)
        return result

    def get_unknown_words_offsets(self, text: str, offsets: list) -> list:
        """
        Add unknown upcase words offset to existing ones
        :param text: original text
        :param offsets: known offset
        :return: offsets as a list
        """
        unknown_offsets = self.get_all_unknown_words_offsets(text=text)
        all_offsets = offsets + unknown_offsets
        return self.clean_unknown_offsets(offsets=all_offsets)

    def get_all_unknown_words_offsets(self, text: str) -> list:
        """
        Find offsets of all words in upcase.
        :param text: original paragraph text
        :return: offsets as a list
        """
        return [(t.start(), t.end(), self.unknown_type_name) for t in self.upcase_words_regex.finditer(text) if
                self.first_name_matcher.contain_first_names(text=text[t.start():t.end()])]

    def clean_unknown_offsets(self, offsets: list) -> list:
        """
        Remove offsets of unknown type span when there is an overlap with a known offset
        :param offsets: cleaned offsets with old known offsets and the new ones
        """
        result = list()
        sorted_offsets = sorted(offsets,
                                key=lambda tup: (tup[0], tup[1]))

        for (index, (start_offset, end_offset, type_name)) in enumerate(sorted_offsets):
            if type_name == self.unknown_type_name:

                # is first token?
                if index > 0:
                    previous_start_offset, previous_end_offset, previous_type_name = sorted_offsets[index - 1]
                else:
                    previous_start_offset, previous_end_offset, previous_type_name = None, None, None

                # is last token?
                if index < len(sorted_offsets) - 1:
                    next_start_offset, next_end_offset, next_type_name = sorted_offsets[index + 1]
                else:
                    next_start_offset, next_end_offset, next_type_name = None, None, None

                is_start_offset_ok = (((previous_end_offset is not None) and (start_offset > previous_end_offset)) or
                                      (previous_end_offset is None))

                is_end_offset_ok = ((next_start_offset is not None) and
                                    (end_offset < next_start_offset) or (next_start_offset is None))

                if is_start_offset_ok and is_end_offset_ok:
                    result.append((start_offset, end_offset, type_name))

            else:
                result.append((start_offset, end_offset, type_name))
        return result
