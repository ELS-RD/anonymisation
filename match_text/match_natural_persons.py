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

extract_partie_pp_pattern_1 = regex.compile(r"([A-Z][\w-\.\s]{0,15})+(?=.{0,5}\sné(e)?\s.{0,5}\d+)",
                                            flags=regex.VERSION1)

extract_partie_pp_pattern_2 = regex.compile(r"(?<=((?i)consorts|époux|docteur|dr(\.)?|professeur|prof(\.)?)\s+)"
                                            r"([A-ZÉÈ]+[\w]*(?:\s[A-ZÉÈ]+[\w]*)*)",
                                            flags=regex.VERSION1)

extract_partie_pp_pattern_3 = regex.compile(r"((?!Madame|Mme(\.)?)[A-ZÉÈ]+[\w]*(?:\s[A-ZÉÈ]+[\w]*)*) (épouse|veuve) "
                                            r"([A-ZÉÈ]+[\w]*(?:\s[A-ZÉÈ]+[\w]*)*)",
                                            flags=regex.VERSION1)


def get_partie_pers(text: str) -> List[Offset]:
    """
    Extract people names from text
    :param text: original paragraph text
    :return: offsets as a list
    """
    result1 = [Offset(start=t.start(), end=t.end(), type="PERS") for t in extract_partie_pp_pattern_1.finditer(text)]
    result2 = [Offset(start=t.start(), end=t.end(), type="PERS") for t in extract_partie_pp_pattern_2.finditer(text)]
    result3 = [Offset(start=t.start(), end=t.end(), type="PERS") for t in extract_partie_pp_pattern_3.finditer(text)]
    return result1 + result2 + result3

