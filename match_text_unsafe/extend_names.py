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

import string
from typing import List

import regex

from match_text.match_address import remove_duplicates
from xml_extractions.extract_node_values import Offset

translator = str.maketrans(string.punctuation, ' ' * len(string.punctuation))  # map punctuation to space


class ExtendNames:
    pattern_title = None
    pattern_extend_right = None
    type_name = None
    dont_detect = True

    def __init__(self, texts: List[str], offsets: List[List[Offset]], type_name: str):
        """
        Extend names to include first and last name when explicitly preceded by Monsieur / Madame
        :param type_name: filter on type name
        :param texts: original text
        :param offsets: discovered offsets from other methods.
        :return: a Regex pattern
        """
        self.type_name = type_name
        extracted_names = set()
        for text, current_offsets in zip(texts, offsets):
            for offset in current_offsets:
                if offset.type == self.type_name:
                    # avoid parentheses and other regex interpreted characters inside the items
                    item: str = text[offset.start:offset.end].translate(translator).strip()
                    if len(item) > 3:
                        extracted_names.add(item)
                    elif (len(item) == 3) and (item[0].isupper()):
                        extracted_names.add(item)

        self.dont_detect = (len(extracted_names) == 0)

        extracted_names_pattern = '|'.join(extracted_names)
        pattern_title = (r"(?<=M\. |\bM\b |Mme |Mlle |(M|m)onsieur |(M|m)adame |(M|m)ademoiselle )"
                         r"("
                         r"("
                         r"(?!\b(M\.)\b |\bM\b |Mme |Mlle |(M|m)onsieur |(M|m)adame |(M|m)ademoiselle )"
                         r"[A-ZÉÈ\-\.]+\w*\s*)*"
                         r"\b(" +
                         extracted_names_pattern +
                         r")\b"
                         r"( [A-ZÉÈ\-\.]+\w*)*"
                         r")")

        pattern_extend_right = (r"\b(" +
                                extracted_names_pattern +
                                r")\b"
                                r"(\s+[A-ZÉÈ\-]+\w*)+")
        self.pattern_title = regex.compile(pattern_title, flags=regex.VERSION1)
        self.pattern_extend_right = regex.compile(pattern_extend_right, flags=regex.VERSION1)

    def get_extended_names(self, text: str) -> List[Offset]:
        """
        Apply the generated regex pattern to current paragraph text
        No computation if there is nothing to find
        :param text: current original text
        :return: offset list
        """
        if self.dont_detect:
            return list()

        result1 = [Offset(t.start(), t.end(), self.type_name) for t in self.pattern_title.finditer(text)]
        result2 = [Offset(t.start(), t.end(), self.type_name) for t in self.pattern_extend_right.finditer(text)]
        result = list(remove_duplicates(result1 + result2))
        result = sorted(result, key=lambda o: o.start)
        return result

    @staticmethod
    def get_extended_extracted_name_multiple_texts(texts: List[str],
                                                   offsets: List[List[Offset]],
                                                   type_name: str) -> List[List[Offset]]:
        """
        Extend known names for a list of texts and offsets
        :param texts: list of original texts
        :param offsets: list of original offsets
        :param type_name: filter on the type name to extend
        :return: a list of extended offsets
        """
        pattern = ExtendNames(texts=texts,
                              offsets=offsets,
                              type_name=type_name)
        result = list()
        for text, offset in zip(texts, offsets):
            current = pattern.get_extended_names(text=text)
            result.append(current + offset)

        return result
