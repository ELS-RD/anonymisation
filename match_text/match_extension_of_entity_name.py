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

from match_text_unsafe.match_acora import AcoraMatcher
from misc.extract_first_last_name import get_first_last_name
from modify_text.modify_strings import remove_org_type
from xml_extractions.extract_node_values import Offset


def get_all_name_variation(texts: List[str], offsets: List[List[Offset]], threshold_span_size: int) ->  List[List[Offset]]:
    """
    Search for any variation of known entities
    :param texts: original text
    :param offsets: discovered offsets
    :param threshold_span_size: minimum size of a name (first / last) to be added to the list
    :return: discovered offsets
    """
    pp_text_span = list()
    pm_text_span = list()
    for current_offsets, text in zip(offsets, texts):
        for offset in current_offsets:
            # start_offset, end_offset, type_name = offset
            text_span = text[offset.start:offset.end].strip()
            if len(text_span) > 0:
                if offset.type == "PERS":
                    pp_text_span.append(text_span)
                    first_name, last_name = get_first_last_name(text_span)
                    first_name = first_name.strip()
                    last_name = last_name.strip()

                    if len(first_name) > threshold_span_size:
                        pp_text_span.append(first_name)
                    if len(last_name) > threshold_span_size:
                        pp_text_span.append(last_name)

                if offset.type == "ORGANIZATION":
                    pm_text_span.append(text_span)
                    short_org_name = remove_org_type(text_span).strip()
                    if (len(short_org_name) > 0) and (short_org_name != text_span):
                        pm_text_span.append(short_org_name)

    pp_matcher = AcoraMatcher(content=pp_text_span, ignore_case=True)
    pm_matcher = AcoraMatcher(content=pm_text_span, ignore_case=True)

    results = list()

    for text, offset in zip(texts, offsets):
        results.append(pp_matcher.get_matches(text=text, tag="PERS") +
                       pm_matcher.get_matches(text=text, tag="ORGANIZATION") +
                       offset)

    return results

