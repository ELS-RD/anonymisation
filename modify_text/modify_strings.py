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
from typing import List, Tuple

import regex

from match_text_unsafe.match_acora import AcoraMatcher

# some organization prefix patterns
from xml_extractions.extract_node_values import Offset

org_types = "société(s)?|" \
            "association|" \
            "s(\.|\s)*a(\.|\s)*s(\.|\s)*u(\.|\s)*|" \
            "e(\.|\s)*u(\.|\s)*r(\.|\s)*l(\.|\s)*|" \
            "e(\.|\s)*i(\.|\s)*r(\.|\s)*l(\.|\s)*|" \
            "e(\.|\s)*a(\.|\s)*r(\.|\s)*l(\.|\s)*|" \
            "a(\.|\s)*a(\.|\s)*r(\.|\s)*p(\.|\s)*i(\.|\s)*|" \
            "s(\.|\s)*c(\.|\s)*s(\.|\s)*|" \
            "s(\.|\s)*n(\.|\s)*c(\.|\s)*|" \
            "s(\.|\s)*e(\.|\s)*m(\.|\s)*|" \
            "s(\.|\s)*c(\.|\s)*p(\.|\s)*|" \
            "s(\.|\s)*a(\.|\s)*s(\.|\s)*|" \
            "s(\.|\s)*a(\.|\s)*|" \
            "s(\.|\s)*a(\.|\s)*s(\.|\s)*u(\.|\s)*|" \
            "s(\.|\s)*a(\.|\s)*r(\.|\s)*l|" \
            "s(\.|\s)*e(\.|\s)*l(\.|\s)*a(\.|\s)*r(\.|\s)*l(\.|\s)*|" \
            "s(\.|\s)*c(\.|\s)*i(\.|\s)*|" \
            "s(\.|\s)*c(\.|\s)*o(\.|\s)*p(\.|\s)*|" \
            "s(\.|\s)*e(\.|\s)*l(\.|\s)*|" \
            "s(\.|\s)*c(\.|\s)*a(\.|\s)*|" \
            "syndic|" \
            "syndicat( des copropriétaires)?|" \
            "(e|é)tablissement|" \
            "mutuelle|" \
            "caisse|" \
            "h.pital|" \
            "clinique|" \
            "banque|" \
            "compagnie( d'assurance)?|" \
            "cabinet"

remove_org_type_pattern = regex.compile("\\b(" + org_types + ")\\b\s+",
                                        flags=regex.VERSION1 | regex.IGNORECASE)


def remove_org_type(original_text: str) -> str:
    """
    Remove corporation type name
    :param original_text: Name of company included its type
    :return: the cleaned string
    """
    return remove_org_type_pattern.sub(repl="", string=original_text).strip()


key_words_matcher = AcoraMatcher(content=["Monsieur", "Madame", "Mme",
                                          "monsieur", "madame",
                                          "la société", "Me", "Maitre", "Maître"],
                                 ignore_case=False)


def remove_key_words(text: str, offsets: List[Offset], rate: int) -> Tuple[str, List[Offset]]:
    """
    Modify text to remove some key words, making the learning harder and the model more robust.
    :param text: original paragraph as a string
    :param offsets: list of extracted offsets
    :param rate: chance as an integer between 1 and 100 that a key word is removed
    :return: a tuple (new_text, offsets)
    """
    words_to_delete_offsets: List[Offset] = key_words_matcher.get_matches(text=text,
                                                                          tag="TO_DELETE")

    if (len(words_to_delete_offsets) == 0) or (len(offsets) == 0):
        return text, offsets

    detected_spans = dict()
    for offset in offsets:
        span_text = text[offset.start:offset.end]
        if len(span_text) > 0:
            detected_spans[span_text] = offset.type

    if len(detected_spans) == 0:
        return text, offsets

    original_content_offsets_matcher = AcoraMatcher(content=list(detected_spans.keys()),
                                                    ignore_case=False)

    cleaned_text = list()
    start_selection_offset = 0
    for offset in words_to_delete_offsets:
        if randint(1, 99) < rate:
            # - 1 to remove also the space following the keyword to remove
            cleaned_text.append(text[start_selection_offset:offset.start - 1])
            start_selection_offset = offset.end
        else:
            cleaned_text.append(text[start_selection_offset:offset.end])
            start_selection_offset = offset.end

    cleaned_text.append(text[start_selection_offset:len(text)])

    cleaned_text = ''.join(cleaned_text)

    updated_offsets = original_content_offsets_matcher.get_matches(text=cleaned_text,
                                                                   tag="UNKNOWN")

    offsets_to_return = list()

    # restore original offset type name
    for offset in updated_offsets:
        span_text = cleaned_text[offset.start:offset.end]
        type_name = detected_spans[span_text]
        offsets_to_return.append(Offset(offset.start, offset.end, type_name))

    return cleaned_text, offsets_to_return
