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

from acora import AcoraBuilder

from xml_extractions.extract_node_values import Offset


class AcoraMatcher:
    matcher = None

    def __init__(self, content: List[str], ignore_case: bool):
        """
        Acora matcher factory
        :param content: a list of items to search
        :param ignore_case: True to match any case
        :return: a built matcher
        """
        # start with a string in case content is empty
        # otherwise it builds a binary Acora matcher
        builder = AcoraBuilder("!@#$%%^&*")
        if len(content) > 0:
            builder.update(content)
        self.matcher = builder.build(ignore_case=ignore_case)

    def get_matches(self, text: str, tag: str) -> List[Offset]:
        """
        Apply the matcher and return offsets
        :param text: original string where to find the matches
        :param tag: the type of offset
        :return: list of offsets
        """
        # matcher not loaded with any pattern
        if self.matcher.__sizeof__() == 0:
            return list()
        results = self.matcher.findall(text)
        return [Offset(start_offset, start_offset + len(match_text), tag)
                for match_text, start_offset in results if
                self.__filter_fake_match(start=start_offset, end=start_offset + len(match_text), text=text)]

    def findall(self, text):
        return self.matcher.findall(text)

    @staticmethod
    def __filter_fake_match(start: int, end: int, text: str) -> bool:
        """
        Predicate to detect if candidate offset is aligned with word boundary
        :param start: begin of the offset
        :param end: end of the offset
        :param text: original text
        :return: True if matches a word boundary
        """
        if start == 0:
            previous_token_ok = True
        else:
            previous_token_ok = not text[start - 1].isalnum()

        if end == len(text):
            next_token_ok = True
        else:
            next_token_ok = not text[end].isalnum()
        return previous_token_ok and next_token_ok
