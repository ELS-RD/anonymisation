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

from xml_extractions.extract_node_values import Offset

extract_rg_from_case_id_pattern = r"(?<=\-)\d*(?=\-jurica$)"
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

    def get_rg_from_case_id(self) -> List[str]:
        """
        Retrieve the RG from case id, as formatted by rule based system
        :return: RG number as a string
        """
        result = extract_rg_from_case_id_regex.findall(self.case_id)
        assert len(result) == 1
        return result[0]

    def get_search_rg_regex(self) -> str:
        """
        Build a regex pattern to find any mention of the RG number corresponding to the one from the rule based case ID
        :return: the pattern as a string
        """
        pattern = [fr"({number}([[:punct:]\s])*)" for number in self.rg[0:len(self.rg) - 1]]
        pattern += self.rg[len(self.rg) - 1]
        pattern = ''.join(pattern)
        pattern = "\\b" + pattern + "\\b"
        return pattern

    def get_rg_offset_from_text(self, text: str) -> List[Offset]:
        """
        Extract RG number offsets from a text, if any
        :param text: original text
        :return: offsets as a list
        """
        return [Offset(item.start(), item.end(), "RG") for item in self.pattern.finditer(text)]

    def get_rg_offset_from_texts(self, texts: List[str], offsets: List[List[Offset]]) -> List[List[Offset]]:
        """
        Extract RG number offsets from a list of texts
        :param texts: original list of texts
        :param offsets: list of offsets
        :return: offsets as a list of lists (including original offsets)
        """
        return [current_offsets + self.get_rg_offset_from_text(text) for text, current_offsets in zip(texts, offsets)]


extract_rg_from_text_pattern = (r"(?<=(\bR[[:punct:]]{0,5}G\b|((?i)répertoire général))"
                                r"[^\d]{0,20})(\d[[:punct:]]*)+( |$)")
extract_rg_from_text_regex = regex.compile(extract_rg_from_text_pattern, flags=regex.VERSION1)


def get_rg_from_regex(text: str) -> List[Offset]:
    """
    Extract RG number from text when some pattern is found
    :param text: original text
    :return: offset as a list
    """
    offsets = extract_rg_from_text_regex.search(text)
    if offsets is not None:
        return [Offset(offsets.start(), offsets.end(), "RG")]
    else:
        return list()
