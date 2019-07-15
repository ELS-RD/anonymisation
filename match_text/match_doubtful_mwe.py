#  Licensed to the Apache Software Foundation (ASF) under one
#  or more contributor license agreements.  See the NOTICE file
#  distributed with this work for additional information
#  regarding copyright ownership.  The ASF licenses this file
#  to you under the Apache License, Version 2.0 (the
#  "License"); you may not use this file except in compliance
#  with the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing,
#  software distributed under the License is distributed on an
#  "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#  KIND, either express or implied.  See the License for the
#  specific language governing permissions and limitations
#  under the License.
from typing import List

import regex

from match_text_unsafe.match_acora import AcoraMatcher
from match_text.match_first_name_dictionary import FirstName
from xml_extractions.extract_node_values import Offset


class MatchDoubfulMwe:
    unknown_type_name = "UNKNOWN"
    pattern = "(?!M\. |\\bM\\b |Mme |Mlle |(M|m)onsieur |(M|m)adame |(M|m)ademoiselle )" \
              "[A-ZÉÈ\-]+\w*" \
              "( [A-ZÉÈ\-]+\w*)*"
    upcase_words_regex = regex.compile(pattern=pattern, flags=regex.VERSION1)
    first_name_matcher = FirstName(ignore_case=False)
    mister_matcher = AcoraMatcher(content=["monsieur", "madame", "Mme ",
                                           "Monsieur", "Madame", " M.", " M ",
                                           " mme "],
                                  ignore_case=False)

    def add_unknown_words_offsets(self, texts: List[str], offsets: List[List[Offset]]) -> List[List[Offset]]:
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

    def get_unknown_words_offsets(self, text: str, offsets: List[Offset]) -> List[Offset]:
        """
        Add unknown upcase words offset to existing ones
        :param text: original text
        :param offsets: known offset
        :return: offsets as a list
        """
        unknown_offsets = self.get_all_unknown_words_offsets(text=text)
        all_offsets = offsets + unknown_offsets
        return self.clean_unknown_offsets(offsets=all_offsets)

    def get_all_unknown_words_offsets(self, text: str) -> List[Offset]:
        """
        Find offsets of all words in upcase.
        :param text: original paragraph text
        :return: offsets as a list
        """
        return [Offset(t.start(), t.end(), self.unknown_type_name) for t in self.upcase_words_regex.finditer(text) if
                self.predicate_keep_unknown_entities(text=text, start=t.start(), end=t.end())]

    def predicate_keep_unknown_entities(self, text: str, start: int, end: int) -> bool:
        """
        Decides if an entity should be kept.
        2 rules : contains a first name or preceded by Mister / Miss / ...
        :param text: original text
        :param start: offset start
        :param end: offset end
        :return: True if entity should be kept
        """
        contain_first_name = self.first_name_matcher.contain_first_names(text=text[start:end])

        if start >= 2:
            new_start = max(0, start - 9)
            previous_token = text[new_start:start]
            contain_mister = len(self.mister_matcher.get_matches(text=previous_token, tag="UNKNOWN")) > 0
        else:
            contain_mister = False

        return contain_first_name or contain_mister

    # TODO rework by removing direct index access
    def clean_unknown_offsets(self, offsets: List[Offset]) -> List[Offset]:
        """
        Remove offsets of unknown type span when there is an overlap with a known offset
        :param offsets: cleaned offsets with old known offsets and the new ones
        """
        result = list()
        sorted_offsets = sorted(offsets,
                                key=lambda o: (o.start, o.end))

        for (index, offset) in enumerate(sorted_offsets):
            start_offset, end_offset, type_name = offset.start, offset.end, offset.type
            if offset.type == self.unknown_type_name:

                # is first token?
                if index > 0:
                    previous_start_offset, previous_end_offset, previous_type_name = sorted_offsets[index - 1].start, \
                                                                                     sorted_offsets[index - 1].end, \
                                                                                     sorted_offsets[index - 1].type
                else:
                    previous_start_offset, previous_end_offset, previous_type_name = None, None, None

                # is last token?
                if index < len(sorted_offsets) - 1:
                    next_start_offset, next_end_offset, next_type_name = sorted_offsets[index + 1].start, \
                                                                         sorted_offsets[index + 1].end, \
                                                                         sorted_offsets[index + 1].type
                else:
                    next_start_offset, next_end_offset, next_type_name = None, None, None

                is_start_offset_ok = (((previous_end_offset is not None) and (start_offset > previous_end_offset)) or
                                      (previous_end_offset is None))

                is_end_offset_ok = ((next_start_offset is not None) and
                                    (end_offset < next_start_offset) or (next_start_offset is None))

                if is_start_offset_ok and is_end_offset_ok:
                    result.append(Offset(start_offset, end_offset, type_name))

            else:
                result.append(Offset(start_offset, end_offset, type_name))
        return result
