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

from random import randint
from typing import List

from xml_extractions.extract_node_values import Offset


def get_title_case(original_text: str) -> str:
    """
    Upper case each first letter of a MWE
    :param original_text: original full name
    :return: transformed string
    """
    return ' '.join([word.capitalize() for word in original_text.split(' ')])


def random_case_change(text: str, offsets: List[Offset], rate: int) -> str:
    """
    Randomly change the case of the string inside the offset to make the NER more robust
    :param text: original text
    :param offsets: original offsets
    :param rate: the percentage of offset to change (as integer)
    :return: the updated text
    """
    for offset in offsets:
        if randint(0, 99) <= rate:
            extracted_content = text[offset.start:offset.end]

            random_transformation = randint(1, 4)
            if random_transformation == 1:
                new_text = extracted_content.lower()
            elif random_transformation == 2:
                new_text = extracted_content.upper()
            elif random_transformation == 3:
                new_text = lower_randomly_word_case(extracted_content)
            else:
                new_text = get_title_case(extracted_content)

            text = text[:offset.start] + new_text + text[offset.end:]

    return text


def lower_randomly_word_case(text: str) -> str:
    """
    Lower randomly the case of some words from the original text.
    Applied only if the entity is made of several words.
    Last word is never lowered case as in real entity.
    :param text: original text
    :return: transformed case text
    """
    words = text.split(' ')
    result = list()
    for word in words:
        action_choice = randint(1, 2)
        if (action_choice == 1) and (len(result) < len(words) - 1):
            result.append(word.lower())
        else:
            result.append(word)
    return ' '.join(result)
